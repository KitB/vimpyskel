if (exists('g:loaded_vimpyskel') && g:loaded_vimpyskel) || &cp
    finish
endif
"let g:loaded_vimpyskel = 1

" --------------------------------
" Add our plugin to the path
" --------------------------------
python import sys
python import vim
python sys.path.append(vim.eval('expand("<sfile>:h")'))

" --------------------------------
"  Function(s)
" --------------------------------
function! vimpyskel#Init()
python << eop

import vimpyskel
vps = vimpyskel.VPSContext()
vps.prepare()

eop
endfunction

function! vimpyskel#TryTemplate()
python << endOfPython

vps()

endOfPython
endfunction

" --------------------------------
"  Expose our commands to the user
" --------------------------------
command! VPSInsert call vimpyskel#TryTemplate()

" --------------------------------
"  Initialize the plugin
" --------------------------------
call vimpyskel#Init()
