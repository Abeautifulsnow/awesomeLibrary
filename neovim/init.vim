call plug#begin('~/.local/share/nvim/plugged')
" tabular
Plug 'godlygeek/tabular'
" 文件管理器
Plug 'scrooloose/nerdtree'
" 注释插件
Plug 'scrooloose/nerdcommenter'
" 主题
Plug 'morhetz/gruvbox'
Plug 'numirias/semshi', {'do' : ':UpdateRemotePlugins'}
" 语法检查
Plug 'neomake/neomake'
" 自动补全
Plug 'Shougo/deoplete.nvim', { 'do': ':UpdateRemotePlugins' }
Plug 'zchee/deoplete-jedi'
" 括号匹配
Plug 'jiangmiao/auto-pairs'
" 状态栏
Plug 'vim-airline/vim-airline'
" 代码自动format
Plug 'sbdchd/neoformat'
" jedi-vim跳转
Plug 'davidhalter/jedi-vim'
" 多点编辑插件
Plug 'terryma/vim-multiple-cursors'
" 代码折叠
Plug 'tmhedberg/SimpylFold'
" markdown插件
Plug 'plasticboy/vim-markdown'
call plug#end()

" nerdtree的配置
autocmd StdinReadPre * let s:std_in=1
autocmd VimEnter * if argc() == 1 && isdirectory(argv()[0]) && !exists("s:std_in") | exe 'NERDTree' argv()[0] | wincmd p | ene | exe 'cd '.argv()[0] | endif

" 主题
colorscheme gruvbox
"set background=dark " 或者 set background=light
" 语法检查 忽视警告
let g:neomake_python_enabled_makers = ['pyflakes']
call neomake#configure#automake('nrwi', 500)	" 自动检查
" 代码补充的键位替换
inoremap <expr><tab> pumvisible() ? "\<c-n>" : "\<tab>"
let g:deoplete#enable_at_startup = 1
" ================================================
" neoformat配置
" Enable alignment
let g:neoformat_basic_format_align = 1
" Enable tab to spaces conversion
let g:neoformat_basic_format_retab = 1
" Enable trimmming of trailing whitespace
let g:neoformat_basic_format_trim = 1
" =================================================
" jedi-vim跳转配置
" disable autocompletion, cause we use deoplete for completion
let g:jedi#completions_enabled = 0
" open the go-to function in split, not another buffer
let g:jedi#use_splits_not_buffers = "right"
" ===============================================
map ,q :call CompileRunGcc()<CR>
" 一键执行
func! CompileRunGcc()
    exec "w"
    if &filetype == 'c'
        exec '!g++ % -o %<'
        exec '!time ./%<'
    elseif &filetype == 'cpp'
        exec '!g++ % -o %<'
        exec '!time ./%<'
    elseif &filetype == 'python'
        exec '!python %'
    elseif &filetype == 'sh'
        :!time bash %
    endif                                                                       
endfunc<Paste>

" 键位的映射
noremap T :NERDTree<CR>
noremap ,l :sp<CR><C-w>j:term ipython<CR> i %run 

set guifont=Courier/20
set foldenable      " 允许折叠  
set showcmd         " 输入的命令显示出来，看的清楚些 
set shortmess=atI   " 启动的时候不显示那个援助乌干达儿童的提示 
" 语法高亮
set syntax=on
" 自动缩进
set autoindent
set cindent
" Tab键的宽度
set tabstop=4
" 匹配括号高亮的时间（单位是十分之一秒）
set matchtime=1
"去掉讨厌的有关vi一致性模式，避免以前版本的一些bug和局限  
set nocompatible
"设置编码
set fileencodings=utf-8,ucs-bom,gb18030,gbk,gb2312,cp936
set termencoding=utf-8
set encoding=utf-8
" 括号匹配
set showmatch
" 鼠标
set mouse=a
set selection=exclusive
set selectmode=mouse,key
" 显示行号
set number
" 设置粘贴
set paste
" 高亮当前行
set cursorline
" 设置空白字符的视觉提示
set list listchars=extends:❯,precedes:❮,tab:▸\ ,trail:-
