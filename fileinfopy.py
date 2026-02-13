""" Written programmatically by Benjamin Jack Cullen """
""" Source and credits to: https://fileinfo.com/ """

import fileinfopy_web_files
import fileinfopy_video_files
import fileinfopy_vector_image_files
import fileinfopy_text_files
import fileinfopy_system_files
import fileinfopy_spreadsheet_files
import fileinfopy_settings_files
import fileinfopy_raster_image_files
import fileinfopy_plugin_files
import fileinfopy_page_layout_files
import fileinfopy_misc_files
import fileinfopy_gis_files
import fileinfopy_game_files
import fileinfopy_font_files
import fileinfopy_executable_files
import fileinfopy_encoded_files
import fileinfopy_disk_image_files
import fileinfopy_developer_files
import fileinfopy_database_files
import fileinfopy_data_files
import fileinfopy_cad_files
import fileinfopy_backup_files
import fileinfopy_audio_files
import fileinfopy_3d_image_files
import cprint
import sys
import unicodedata
import tabulate_helper2

web_files = fileinfopy_web_files.web_files
video_files = fileinfopy_video_files.video_files
vector_image_files = fileinfopy_vector_image_files.vector_image_files
three_d_image_files = fileinfopy_3d_image_files.three_d_image_files
text_files = fileinfopy_text_files.text_files
system_files = fileinfopy_system_files.system_files
spreadsheet_files = fileinfopy_spreadsheet_files.spreadsheet_files
settings_files = fileinfopy_settings_files.settings_files
raster_image_files = fileinfopy_raster_image_files.raster_image_files
plugin_files = fileinfopy_plugin_files.plugin_files
page_layout_files = fileinfopy_page_layout_files.page_layout_files
misc_files = fileinfopy_misc_files.misc_files
gis_files = fileinfopy_gis_files.gis_files
game_files = fileinfopy_game_files.game_files
font_files = fileinfopy_font_files.font_files
executable_files = fileinfopy_executable_files.executable_files
encoded_files = fileinfopy_encoded_files.encoded_files
disk_image_files = fileinfopy_disk_image_files.disk_image_files
developer_files = fileinfopy_developer_files.developer_files
database_files = fileinfopy_database_files.database_files
data_files = fileinfopy_data_files.data_files
cad_files = fileinfopy_cad_files.cad_files
backup_files = fileinfopy_backup_files.backup_files
audio_files = fileinfopy_audio_files.audio_files
all_files = [audio_files, backup_files, cad_files, data_files, database_files, developer_files, disk_image_files,
             encoded_files, executable_files, font_files, game_files, gis_files, misc_files, page_layout_files,
             plugin_files, raster_image_files, settings_files, spreadsheet_files, system_files, text_files,
             three_d_image_files, vector_image_files, video_files, web_files]

# use color: removes all color byte sequences which may be useful sometimes depending on how this program is run.
NO_COLOR = False

# make true to enable test mode
_DEBUG = False

# verbosity: say more if enabled
_VERBOSE = False

# interact: enable to prevent results being lost in a small terminal/console buffer
_INTERACT = False


# ------------------------- STRINGS
def NFD(text):
    return unicodedata.normalize('NFD', text)


def canonical_caseless(text):
    return NFD(NFD(text).casefold())


def _display(_extensions):
    print('')
    print('')
    if NO_COLOR is False:

        # display result
        print(str(cprint.color(s=f'[  Category     ]  {_extensions[0].replace("_", " ").title()}', c='BL')))
        print(str(cprint.color(s=f'[  Extension    ]  {_extensions[1]}', c='BL')))
        print(str(cprint.color(s=f'[  File Type    ]  {_extensions[2]}', c='BL')))

        # display description: limit description length for some output clarity
        max_w = tabulate_helper2.column_width_from_shutil(n=1, reduce=0, add=0) - 24
        _description = tabulate_helper2.chunk_data(data=_extensions[4], chunk_size=max_w)
        if _description[0].startswith(' '):
            _description[0] = _description[0][1:]
        print(str(cprint.color(s=f'[  Description  ]  {_description[0]}', c='BL')))

        # display description: iterate over chunks of description
        _i_desc = 0
        for _descriptions in _description:
            if _i_desc != 0:
                if _descriptions.startswith(' '):
                    # display description: remove any leading space
                    _descriptions = _descriptions[1:]
                print(' '*19 + str(cprint.color(s=f'{_descriptions}', c='BL')))
            _i_desc += 1

        # display software: iterate over chunks of description
        if _extensions[5]:
            _description = tabulate_helper2.chunk_data(data=_extensions[5], chunk_size=max_w)
            if _description[0].startswith(' '):
                _description[0] = _description[0][1:]
            print(str(cprint.color(s=f'[  Association  ]  {_description[0]}', c='BL')))
            # display software: iterate over chunks of description
            _i_desc = 0
            for _descriptions in _description:
                if _i_desc != 0:
                    if _descriptions.startswith(' '):
                        # display software: remove any leading space
                        _descriptions = _descriptions[1:]
                    print(' '*19 + str(cprint.color(s=f'{_descriptions}', c='BL')))
                _i_desc += 1

        # display formats: iterate over chunks of description
        if _extensions[6]:
            _description = tabulate_helper2.chunk_data(data=_extensions[6], chunk_size=max_w)
            if _description[0].startswith(' '):
                _description[0] = _description[0][1:]
            print(str(cprint.color(s=f'[  Conversion   ]  {_description[0]}', c='BL')))
            # display software: iterate over chunks of description
            _i_desc = 0
            for _descriptions in _description:
                if _i_desc != 0:
                    if _descriptions.startswith(' '):
                        # display software: remove any leading space
                        _descriptions = _descriptions[1:]
                    print(' '*19 + str(cprint.color(s=f'{_descriptions}', c='BL')))
                _i_desc += 1

    else:
        # display result
        print(f'[  Category     ]  {_extensions[0].replace("_", " ").title()}')
        print(f'[  Extension    ]  {_extensions[1]}')
        print(f'[  File Type    ]  {_extensions[2]}')
        # display description: limit description length for some output clarity
        max_w = tabulate_helper2.column_width_from_shutil(n=1, reduce=0, add=0) - 26
        _description = tabulate_helper2.chunk_data(data=_extensions[4], chunk_size=max_w)
        if _description[0].startswith(' '):
            # display formats: remove any leading space
            _description[0] = _description[0][1:]
        print(f'[  Description  ]  {_description[0]}')
        # display description: iterate over chunks of description
        _i_desc = 0
        for _descriptions in _description:
            if _i_desc != 0:
                if _descriptions.startswith(' '):
                    # display description: remove any leading space
                    _descriptions = _descriptions[1:]
                print(' '*19 + _descriptions)
            _i_desc += 1

        # display software: iterate over chunks of description
        if _extensions[5]:
            _description = tabulate_helper2.chunk_data(data=_extensions[5], chunk_size=max_w)
            if _description[0].startswith(' '):
                # display formats: remove any leading space
                _description[0] = _description[0][1:]
            print(f'[  Association  ]  {_description[0]}')
            # display software: iterate over chunks of description
            _i_desc = 0
            for _descriptions in _description:
                if _i_desc != 0:
                    if _descriptions.startswith(' '):
                        # display software: remove any leading space
                        _descriptions = _descriptions[1:]
                    print(' '*19 + _descriptions)
                _i_desc += 1

        if _extensions[6]:
            # display formats: iterate over chunks of description
            _description = tabulate_helper2.chunk_data(data=_extensions[6], chunk_size=max_w)
            if _description[0].startswith(' '):
                # display formats: remove any leading space
                _description[0] = _description[0][1:]
            print(f'[  Conversion   ]  {_description[0]}')
            # display formats: iterate over chunks of description
            _i_desc = 0
            for _descriptions in _description:
                if _i_desc != 0:
                    if _descriptions.startswith(' '):
                        # display formats: remove any leading space
                        _descriptions = _descriptions[1:]
                    print(' '*19 + _descriptions)
                _i_desc += 1

    if _INTERACT is True:
        try:
            input()
        except KeyboardInterrupt:
            print('\n')
            exit(0)


stdin = sys.argv
# uncomment to enable debug argument (for testing): enabling debug turns off string matching (return everything).
if '--debug' in stdin:
    _DEBUG = True
# compatibility: no cprint option for further potential compatibility across different (untested) systems.
if '--no-color' in stdin:
    NO_COLOR = True
# search in description for -s and in suffix for -s.
if '-v' in stdin:
    _VERBOSE = True
# prompt between each result.
if '-I' in stdin:
    _INTERACT = True

# display help.
if '-h' in stdin and NO_COLOR is True:
    print('')
    print('')
    print('[FILEINFO]')
    print('')
    print(' -s           Search     Search for suffix.')
    print(' -v           Verbose    Search suffix and search descriptions for -s (Used with -s).')
    print(' -I           Interact   Prompted results. Useful when results may exceed terminal buffer size.')
    print(' --no-color   No Color   Disable color printing (make compatible on different systems).')
    print(' -h           Help       Display this help message.')
    print('')
    print(' Developer: Written programmatically by Benjamin Jack Cullen.')
    print(' Information source: https://www.fileinfo.com')
    print('')
    print('')
elif '-h' in stdin and NO_COLOR is False:
    print('')
    print('')
    print(str(cprint.color(s=f'[FILEINFO]', c='BL')))
    print('')
    print(str(cprint.color(s=f' -s           Search     Search for suffix.', c='BL')))
    print(str(cprint.color(s=f' -v           Verbose    Search suffix and search descriptions for -s (Used with -s).', c='BL')))
    print(str(cprint.color(s=f' -I           Interact   Prompted results. Useful when results may exceed terminal buffer size.', c='BL')))
    print(str(cprint.color(s=f' --no-color   No Color   Disable color printing (make compatible on different systems).', c='BL')))
    print(str(cprint.color(s=f' -h           Help       Display this help message.', c='BL')))
    print('')
    print(str(cprint.color(s=f' Developer: Written programmatically by Benjamin Jack Cullen.', c='BL')))
    print(str(cprint.color(s=f' Data Source: https://www.fileinfo.com', c='BL')))
    print('')
    print('')

# search by suffix and if verbose then also search description
elif '-s' in stdin:
    _ext = stdin[stdin.index('-s')+1]
    for sublist in all_files:
        for _extensions in sublist:
            if canonical_caseless(_extensions[1]).replace('.', '') == canonical_caseless(_ext).replace('.', ''):
                _display(_extensions)
    if _VERBOSE is True:
        for sublist in all_files:
            for _extensions in sublist:
                if canonical_caseless(_ext).replace('.', '') in canonical_caseless(_extensions[4]).replace('.', ''):
                    _display(_extensions)
    print('\n\n')

# list definitions
elif '-l' in stdin and NO_COLOR is False:
    print('')
    print('')
    print(str(cprint.color(s=f'[FILEINFO] Definition list...', c='BL')))
    print('')
    for sublist in all_files:
        print(str(cprint.color(s=f'[{sublist[0][0].upper().replace("_", " ")}] {len(sublist)}', c='BL')))
    print('\n\n')
elif '-l' in stdin and NO_COLOR is True:
    print('')
    print('')
    print(f'[FILEINFO] Definition list...')
    print('')
    for sublist in all_files:
        print(f'[CATEGORY] {sublist[0][0].upper().replace("_", "")}: {len(sublist)} entries.')
    print('\n\n')

# simulates and tests display of every possible result (no break pass test).
elif '--debug' in stdin:
    for sublist in all_files:
        for _extensions in sublist:
            _display(_extensions)
    print('\n\n')

