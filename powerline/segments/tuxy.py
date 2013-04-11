import os
from powerline.lib.threaded import with_docstring
from powerline.lib.vcs import guess
from powerline.theme import requires_segment_info
import powerline.segments.common as common
import shlex

def _run_cmd(cmd):
    from subprocess import Popen, PIPE
    try:
        p = Popen(cmd, stdout=PIPE)
        stdout, err = p.communicate()
    except OSError as e:
        sys.stderr.write('Could not execute command ({0}): {1}\n'.format(e, cmd))
        return None
    if stdout:
        return stdout.decode('utf-8').strip()
    return None


@requires_segment_info
class TmuxInfo:
    pane_info = 0

    @classmethod
    def update_pane_info(cls):
        if cls.pane_info == 0:
            tmux_cmd = 'tmux display-message -p ' + \
                       '"#{session_name}_#{window_index}_#{pane_index}"'
            cls.pane_info = _run_cmd(shlex.split(tmux_cmd))
        return None

    @classmethod
    def has_tmux(cls, segment_info):
        return segment_info['environ'].get('TMUX') and (cls.update_pane_info() or cls.pane_info)

    @classmethod
    def get_env_var(cls, env_var):
        tmux_var = 'POWERLINE_' + cls.pane_info + '_' + env_var
        val = _run_cmd(shlex.split('tmux show-environment ' + tmux_var))
        if val is not None:
            val = val.split('=',1)[1]
            if val != '':
                return val
        return None


class RepositoryStatusSegment(common.RepositoryStatusSegment):

    @staticmethod
    def key(segment_info, **kwargs):
        if TmuxInfo.has_tmux(segment_info):
            return (TmuxInfo.get_env_var('BRANCHNAME'),
                    os.path.abspath(TmuxInfo.get_env_var('PWD')))
        else:
            return (segment_info['environ'].get('BRANCHNAME'),
                    os.path.abspath(segment_info['getcwd']()))

    def compute_state(self, branch_name_path):
        if branch_name_path[0]:
            return True
        else:
            return super(RepositoryStatusSegment,
                         self).compute_state(branch_name_path[1])


repository_status = with_docstring(RepositoryStatusSegment(),
'''Return the status for the current VCS repository.''')


class BranchSegment(common.BranchSegment):
    started_branch_repository_status = False

    @staticmethod
    def key(segment_info, **kwargs):
        if TmuxInfo.has_tmux(segment_info):
            return (TmuxInfo.get_env_var('BRANCHNAME'),
                    os.path.abspath(TmuxInfo.get_env_var('PWD')))
        else:
            return (segment_info['environ'].get('BRANCHNAME'),
                    os.path.abspath(segment_info['getcwd']()))

    def compute_state(self, branch_name_path):
        if branch_name_path[0]:
            return branch_name_path[0]
        else:
            return super(BranchSegment,
                         self).compute_state(branch_name_path[1])

    @staticmethod
    def render_one(branch, status_colors=False, **kwargs):
        if branch and status_colors:
            return [{
                'contents': branch,
                'highlight_group': ['branch_dirty' if repository_status(**kwargs) else 'branch_clean', 'branch'],
            }]
        else:
            return branch

    def startup(self, status_colors=False, **kwargs):
        super(BranchSegment, self).startup(**kwargs)
        if status_colors:
            self.started_branch_repository_status = True
            repository_status.startup(**kwargs)

    def shutdown(self):
        if self.started_branch_repository_status:
            repository_status.shutdown()
        super(BranchSegment, self).shutdown()


branch = with_docstring(BranchSegment(),
'''Tmux safe version of returning the current VCS branch.@

:param bool status_colors:
determines whether repository status will be used to determine highlighting.
Default: True.

Highlight groups used: ``branch_clean``, ``branch_dirty``, ``branch``.
''')


@requires_segment_info
def virtualenv(pl, segment_info):
    '''Tmux safe version of returning the name of the current Python virtualenv.'''
    if TmuxInfo.has_tmux(segment_info):
        virtual_env_var = TmuxInfo.get_env_var('VIRTUAL_ENV')
        if virtual_env_var is not None:
            return os.path.basename(virtual_env_var)
    else:
        return common.virtualenv(pl, segment_info)
    return None


@requires_segment_info
def sandbox_id(pl, segment_info):
    if TmuxInfo.has_tmux(segment_info):
        return TmuxInfo.get_env_var('SANDBOX_ID')
    else:
        return segment_info['environ'].get('SANDBOX_ID')


@requires_segment_info
def sandbox_flavor(pl, segment_info):
    if TmuxInfo.has_tmux(segment_info):
        return TmuxInfo.get_env_var('FLAVOR')
    else:
        return segment_info['environ'].get('FLAVOR')


def spacer(pl):
    return ''
