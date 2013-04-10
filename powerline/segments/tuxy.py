import os
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
    return stdout.strip()

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

@requires_segment_info
def branch(status_colors=True):
    '''Tmux safe version of returning the current VCS branch.@

    :param bool status_colors:
    determines whether repository status will be used to determine highlighting.
    Default: True.

    Highlight groups used: ``branch_clean``, ``branch_dirty``, ``branch``.
    '''
    if TmuxInfo.has_tmux(segment_info):
        # Check if it is a Perforce branch
        branch_name = TmuxInfo.get_env_var('BRANCHNAME')
        if branch_name is not None:
            return [{
                        'contents' : branch_name,
                        'highlight_group' : 'branch_dirty'
                    }]

        # Try other VCSs next
        cwd = TmuxInfo.get_env_var('PWD')
        if cwd is not None:
            repo = guess(path=cwd)
            if repo:
                branch_name = repo.branch()
                if status_colors:
                    return [{
                                'contents': branch_name,
                                'highlight_group': ['branch_dirty' if repo.status() else 'branch_clean', 'branch'],
                            }]
                else:
                    return branch_name
    else:
        # Check if it is a Perforce branch
        branch_name = segment_info['environ'].get('BRANCHNAME')
        if branch_name is not None:
            return [{
                        'contents' : branch_name,
                        'highlight_group' : 'branch_dirty'
                    }]
        else:
            return common.branch(status_colors)
    return None

@requires_segment_info
def virtualenv(pl, segment_info):
    '''Tmux safe version of returning the name of the current Python virtualenv.'''
    if TmuxInfo.has_tmux(segment_info):
        virtual_env_var = TmuxInfo.get_env_var('VIRTUAL_ENV')
        if virtual_env_var is not None:
            return os.path.basename(virtual_env_var)
    else:
        return common.virtualenv()
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

@requires_segment_info
def spacer(pl, segment_info):
    return ''
