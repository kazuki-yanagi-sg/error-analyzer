# Error Summarizer Auto-Wrapper for Zsh
# Sources this file in your .zshrc to enable automatic error analysis.

# Path to the wrapper script (absolute path)
# We assume this script is in src/ relative to the project root
_ES_PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-${(%):-%x}}")/.." && pwd)"
_ES_WRAPPER="${_ES_PROJECT_DIR}/w.sh"

# List of commands to exclude from wrapping
# These are typically interactive commands, editors, or shell builtins
_ES_EXCLUDED_COMMANDS=(
    "cd" "pushd" "popd" "source" "." "export" "alias" "unalias" "declare" "typeset" "local"
    "vim" "vi" "nano" "emacs" "code" "cursor"
    "man" "less" "more" "tail" "head"
    "ssh" "scp" "sftp"
    "top" "htop" "btop"
    "docker" "docker-compose" # Often interactive or produce complex output streams
    "git" # Git has its own error handling, usually doesn't need full RAG analysis for simple typos
    "w" # Don't wrap the wrapper
    "exit" "logout" "clear" "history"
)

# Function to check if a command should be excluded
_es_should_exclude() {
    local cmd="$1"
    # Get the first word (the command itself)
    local base_cmd="${cmd%% *}"
    
    # Check if it's in the exclusion list
    if [[ " ${_ES_EXCLUDED_COMMANDS[@]} " =~ " ${base_cmd} " ]]; then
        return 0 # True, exclude
    fi
    
    # Check if it's a variable assignment (e.g., VAR=val)
    if [[ "$base_cmd" =~ = ]]; then
        return 0
    fi
    
    return 1 # False, don't exclude
}

# ZLE Widget to intercept Enter key
_auto_error_summarizer_accept_line() {
    # Get the current buffer (command line)
    local cmd="${BUFFER}"
    
    # Trim whitespace
    cmd="${cmd#"${cmd%%[![:space:]]*}"}"
    
    # If buffer is empty, just accept
    if [[ -z "$cmd" ]]; then
        zle .accept-line
        return
    fi
    
    # Check exclusion
    if ! _es_should_exclude "$cmd"; then
        # Check if already wrapped (simple check)
        if [[ "$cmd" != "${_ES_WRAPPER}"* ]]; then
            # Prepend the wrapper
            BUFFER="${_ES_WRAPPER} ${BUFFER}"
        fi
    fi
    
    # Execute the command
    zle .accept-line
}

# Register the widget
zle -N accept-line _auto_error_summarizer_accept_line
