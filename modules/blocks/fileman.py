"""
External block example for modular Streamlit page framework.
"""
import streamlit as st

def fileman():
    # st.subheader("fileman.py   Block header")
    # st.write("fileman.py file!")
    # st.snow()
    # HISTORY:
    # 2025-04-30 Print /app/data directory contents in ls -l format for Streamlit
    # 2025-04-30 Refactor: allow browsing any folder starting from /app, with input box and clickable folders
    # 2025-04-30 Add: clickable 'go up' icon and clickable folder names in listing
    # 2025-04-30 Improve: better layout for clickable folders in listing (single column, inline buttons)
    # 2025-04-30 Improve: use two-column layout per row for perfect alignment
    # 2025-04-30 Improve: order listing with directories first, then files, both alphabetically

    import os
    import stat
    import datetime

    def format_permissions(mode):
        is_dir = 'd' if stat.S_ISDIR(mode) else '-'
        perm = ''
        for who in ['USR', 'GRP', 'OTH']:
            for what in ['R', 'W', 'X']:
                perm += (mode & getattr(stat, f'S_I{what}{who}')) and what.lower() or '-'
        return is_dir + perm

    def list_dir_ls_l(path):
        entries = []
        dir_entries = []
        file_entries = []
        folders = []
        try:
            for entry in os.scandir(path):
                stat_info = entry.stat()
                perms = format_permissions(stat_info.st_mode)
                nlink = stat_info.st_nlink
                owner = 'root'  # Or use pwd.getpwuid if available
                group = 'root'  # Or use grp.getgrgid if available
                size = stat_info.st_size
                mtime = datetime.datetime.fromtimestamp(stat_info.st_mtime).strftime('%b %d %H:%M')
                name = entry.name
                entry_dict = {
                    'display': f"{perms} {nlink} {owner} {group} {size:8} {mtime}",
                    'is_dir': entry.is_dir(),
                    'folder': entry.name if entry.is_dir() else None,
                    'name': entry.name
                }
                if entry.is_dir():
                    entry_dict['name'] += '/'
                    folders.append(entry.name)
                    dir_entries.append(entry_dict)
                else:
                    file_entries.append(entry_dict)
            # Sort directories and files alphabetically by name (case-insensitive)
            dir_entries_sorted = sorted(dir_entries, key=lambda x: x['name'].lower())
            file_entries_sorted = sorted(file_entries, key=lambda x: x['name'].lower())
            entries = dir_entries_sorted + file_entries_sorted
        except Exception as e:
            entries.append({'display': f"Error reading directory: {e}", 'is_dir': False, 'folder': None, 'name': None})
        return entries, folders

    # --- Streamlit UI for browsing directories ---
    st.write("## Directory Browser")
    default_path = '/app'
    if 'current_path' not in st.session_state:
        st.session_state.current_path = default_path

    input_path = st.text_input('Enter directory path', st.session_state.current_path)
    if input_path != st.session_state.current_path:
        st.session_state.current_path = input_path

    entries, folders = list_dir_ls_l(st.session_state.current_path)

    # --- Go Up Icon/Button ---
    col_up, col_title = st.columns([1, 10])
    with col_up:
        parent_path = os.path.dirname(st.session_state.current_path.rstrip('/'))
        show_up = st.session_state.current_path not in ['/', default_path]
        if show_up:
            if st.button('⬆️', help='Go up one folder', key='go_up'):
                if parent_path:
                    st.session_state.current_path = parent_path if parent_path != '' else '/'
                    st.rerun()
    with col_title:
        st.write(f"Contents of {st.session_state.current_path}:")

    # --- Improved Directory Listing: two columns per row for alignment ---
    for entry in entries:
        if entry['is_dir'] and entry['folder']:
            col_btn, col_txt = st.columns([2, 10])
            with col_btn:
                if st.button(f"📁 {entry['folder']}/", key=f'navinline_{entry["folder"]}_{st.session_state.current_path}', help='Open folder', use_container_width=True):
                    next_path = os.path.join(st.session_state.current_path, entry['folder'])
                    next_path = os.path.normpath(next_path)
                    st.session_state.current_path = next_path
                    st.rerun()
            with col_txt:
                st.markdown(f"<span style='font-family:monospace'>{entry['display']} <span style='color:#3A8EBA;font-weight:bold'>{entry['folder']}/</span></span>", unsafe_allow_html=True)
        else:
            # File: just show ls -l info and filename
            col_btn, col_txt = st.columns([2, 10])
            with col_btn:
                st.write("")  # empty for files
            with col_txt:
                st.markdown(f"<span style='font-family:monospace'>{entry['display']} <span style='color:#888'>{entry['name']}</span></span>", unsafe_allow_html=True)

# fileman()