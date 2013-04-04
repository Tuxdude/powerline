import os
from powerline.lib.vcs import guess
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

class TmuxInfo:
    pane_info = 0

    @classmethod
    def update_pane_info(cls):
        if cls.pane_info == 0:
            cls.pane_info = _run_cmd(shlex.split('tmux display-message -p "#S_#I_#P"'))
        return None

    @classmethod
    def has_tmux(cls):
        return os.environ.get('TMUX') and (cls.update_pane_info() or cls.pane_info)

    @classmethod
    def get_env_var(cls, env_var):
        tmux_var = 'POWERLINE_' + cls.pane_info + '_' + env_var
        val = _run_cmd(shlex.split('tmux show-environment ' + tmux_var))
        if val is not None:
            val = val.split('=',1)[1]
            if val != '':
                return val
        return None

def branch(status_colors=True):
    '''Tmux safe version of returning the current VSC branch.@

    :param bool status_colors:
    determines whether repository status will be used to determine highlighting. Default: True.

    Highlight groups used: ``branch_clean``, ``branch_dirty``, ``branch``.
    '''
    if TmuxInfo.has_tmux():
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
        return common.branch(status_colors)
    return None

def virtualenv():
    '''Tmux safe version of returning the name of the current Python virtualenv.'''
    if TmuxInfo.has_tmux():
        virtual_env_var = TmuxInfo.get_env_var('VIRTUAL_ENV')
        if virtual_env_var is not None:
            return os.path.basename(virtual_env_var)
    else:
        return common.virtualenv()
    return None

def sandbox_id():
    if TmuxInfo.has_tmux():
        return TmuxInfo.get_env_var('SANDBOX_ID')
    else:
        return os.environ.get('SANDBOX_ID')

def sandbox_perforce_branch_name():
    if TmuxInfo.has_tmux():
        return TmuxInfo.get_env_var('BRANCHNAME')
    else:
        return os.environ.get('BRANCHNAME')

def sandbox_flavor():
    if TmuxInfo.has_tmux():
        return TmuxInfo.get_env_var('FLAVOR')
    else:
        return os.environ.get('FLAVOR')

def spacer():
    return ''
