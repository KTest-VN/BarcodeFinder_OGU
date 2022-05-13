#############################################################################
# Generated by PAGE version 7.4
#  in conjunction with Tcl version 8.6
#  May 13, 2022 10:24:02 PM CST  platform: Windows NT
set vTcl(timestamp) ""
if {![info exists vTcl(borrow)]} {
    ::vTcl::MessageBox -title Error -message  "You must open project files from within PAGE."
    exit}


set image_list { 
    button4_png "./button4.png" 
    button1_png "./button1.png" 
    button2_png "./button2.png" 
    button3_png "./button3.png" 
}
vTcl:create_project_images $image_list   ;# In image.tcl

if {!$vTcl(borrow) && !$vTcl(template)} {

set vTcl(actual_gui_font_dft_desc)  TkDefaultFont
set vTcl(actual_gui_font_dft_name)  TkDefaultFont
set vTcl(actual_gui_font_text_desc)  TkTextFont
set vTcl(actual_gui_font_text_name)  TkTextFont
set vTcl(actual_gui_font_fixed_desc)  TkFixedFont
set vTcl(actual_gui_font_fixed_name)  TkFixedFont
set vTcl(actual_gui_font_menu_desc)  TkMenuFont
set vTcl(actual_gui_font_menu_name)  TkMenuFont
set vTcl(actual_gui_font_tooltip_desc)  TkDefaultFont
set vTcl(actual_gui_font_tooltip_name)  TkDefaultFont
set vTcl(actual_gui_font_treeview_desc)  TkDefaultFont
set vTcl(actual_gui_font_treeview_name)  TkDefaultFont
########################################### 
set vTcl(actual_gui_bg) #d9d9d9
set vTcl(actual_gui_fg) #000000
set vTcl(actual_gui_analog) #ececec
set vTcl(actual_gui_menu_analog) #ececec
set vTcl(actual_gui_menu_bg) #d9d9d9
set vTcl(actual_gui_menu_fg) #000000
set vTcl(complement_color) #d9d9d9
set vTcl(analog_color_p) #d9d9d9
set vTcl(analog_color_m) #ececec
set vTcl(tabfg1) black
set vTcl(tabfg2) black
set vTcl(actual_gui_menu_active_bg)  #ececec
set vTcl(actual_gui_menu_active_fg)  #000000
########################################### 
set vTcl(pr,autoalias) 1
set vTcl(pr,relative_placement) 1
set vTcl(mode) Relative
}




proc vTclWindow.top44 {base} {
    global vTcl
    if {$base == ""} {
        set base .top44
    }
    if {[winfo exists $base]} {
        wm deiconify $base; return
    }
    set top $base
    set target $base
    ###################
    # CREATING WIDGETS
    ###################
    vTcl::widgets::core::toplevel::createCmd $top -class Toplevel \
        -menu "$top.m52" -background #edf0f3 \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black 
    wm focusmodel $top passive
    wm geometry $top 800x451+374+81
    update
    # set in toplevel.wgt.
    global vTcl
    global img_list
    set vTcl(save,dflt,origin) 0
    wm maxsize $top 2564 1421
    wm minsize $top 120 1
    wm overrideredirect $top 0
    wm resizable $top 1 1
    wm deiconify $top
    set toptitle "BarcodeFinder"
    wm title $top $toptitle
    namespace eval ::widgets::${top}::ClassOption {}
    set ::widgets::${top}::ClassOption(-toptitle) $toptitle
    vTcl:DefineAlias "$top" "main" vTcl:Toplevel:WidgetProc "" 1
    set vTcl(real_top) {}
    vTcl:withBusyCursor {
    checkbutton $top.che55 \
        -activebackground $vTcl(analog_color_m) -activeforeground #000000 \
        -background #edf0f0 -disabledforeground #a3a3a3 \
        -font {-family TkDefaultFont -size 15 -weight normal -slant roman -underline 0 -overstrike 0} \
        -foreground $vTcl(actual_gui_fg) \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black \
        -justify left -text GB2Fasta -variable che1 
    vTcl:DefineAlias "$top.che55" "run_gb2fasta" vTcl:WidgetProc "main" 1
    checkbutton $top.che56 \
        -activebackground $vTcl(analog_color_m) -activeforeground #000000 \
        -background #edf0f0 -disabledforeground #a3a3a3 \
        -font {-family TkDefaultFont -size 15 -weight normal -slant roman -underline 0 -overstrike 0} \
        -foreground $vTcl(actual_gui_fg) \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black \
        -justify left -text Evaluate -variable che2 
    vTcl:DefineAlias "$top.che56" "run_evaluate" vTcl:WidgetProc "main" 1
    checkbutton $top.che57 \
        -activebackground $vTcl(analog_color_m) -activeforeground #000000 \
        -background #edf0f0 -disabledforeground #a3a3a3 \
        -font {-family TkDefaultFont -size 15 -weight normal -slant roman -underline 0 -overstrike 0} \
        -foreground $vTcl(actual_gui_fg) \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black \
        -justify left -text Primer -variable che3 
    vTcl:DefineAlias "$top.che57" "run_primer" vTcl:WidgetProc "main" 1
    button $top.but46 \
        -activebackground $vTcl(analog_color_m) -activeforeground #000000 \
        -background $vTcl(actual_gui_bg) -borderwidth 1 -command run_help \
        -disabledforeground #a3a3a3 -font TkDefaultFont \
        -foreground $vTcl(actual_gui_fg) \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black \
        -image button4_png -pady 0 -text Button 
    vTcl:DefineAlias "$top.but46" "help_b" vTcl:WidgetProc "main" 1
    button $top.but47 \
        -activebackground $vTcl(analog_color_m) -activeforeground #000000 \
        -background $vTcl(actual_gui_bg) -borderwidth 0 -command run_gb2fasta \
        -disabledforeground #a3a3a3 -font TkDefaultFont \
        -foreground $vTcl(actual_gui_fg) \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black \
        -image button1_png -pady 0 -text Button 
    vTcl:DefineAlias "$top.but47" "gb2fasta_b" vTcl:WidgetProc "main" 1
    button $top.but48 \
        -activebackground $vTcl(analog_color_m) -activeforeground #000000 \
        -background $vTcl(actual_gui_bg) -borderwidth 0 -command run_evaluate \
        -disabledforeground #a3a3a3 -font TkDefaultFont \
        -foreground $vTcl(actual_gui_fg) \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black \
        -image button2_png -pady 0 -text Button 
    vTcl:DefineAlias "$top.but48" "evaluate_b" vTcl:WidgetProc "main" 1
    button $top.but49 \
        -activebackground $vTcl(analog_color_m) -activeforeground #000000 \
        -background $vTcl(actual_gui_bg) -borderwidth 0 -command run_primer \
        -disabledforeground #a3a3a3 -font TkDefaultFont \
        -foreground $vTcl(actual_gui_fg) \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black \
        -image button3_png -pady 0 -text Button 
    vTcl:DefineAlias "$top.but49" "primer_b" vTcl:WidgetProc "main" 1
    button $top.but55 \
        -activebackground $vTcl(analog_color_m) -activeforeground #000000 \
        -background #edf0f3 -borderwidth 1 -compound left \
        -disabledforeground #a3a3a3 \
        -font {-family {Microsoft YaHei UI} -size 14 -weight normal -slant roman -underline 0 -overstrike 0} \
        -foreground $vTcl(actual_gui_fg) \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black \
        -pady 0 -text Run 
    vTcl:DefineAlias "$top.but55" "Button2" vTcl:WidgetProc "main" 1
    ###################
    # SETTING GEOMETRY
    ###################
    place $top.che55 \
        -in $top -x 0 -relx 0.163 -y 0 -rely 0.533 -width 0 -relwidth 0.164 \
        -height 0 -relheight 0.067 -anchor nw -bordermode ignore 
    place $top.che56 \
        -in $top -x 0 -relx 0.413 -y 0 -rely 0.533 -width 0 -relwidth 0.165 \
        -height 0 -relheight 0.067 -anchor nw -bordermode ignore 
    place $top.che57 \
        -in $top -x 0 -relx 0.663 -y 0 -rely 0.533 -width 0 -relwidth 0.165 \
        -height 0 -relheight 0.067 -anchor nw -bordermode ignore 
    place $top.but46 \
        -in $top -x 0 -relx 0.913 -y 0 -rely 0.067 -width 40 -relwidth 0 \
        -height 40 -relheight 0 -anchor nw -bordermode ignore 
    place $top.but47 \
        -in $top -x 0 -relx 0.188 -y 0 -rely 0.289 -width 100 -relwidth 0 \
        -height 100 -relheight 0 -anchor nw -bordermode ignore 
    place $top.but48 \
        -in $top -x 0 -relx 0.438 -y 0 -rely 0.289 -width 100 -relwidth 0 \
        -height 100 -relheight 0 -anchor nw -bordermode ignore 
    place $top.but49 \
        -in $top -x 0 -relx 0.688 -y 0 -rely 0.289 -width 100 -relwidth 0 \
        -height 100 -relheight 0 -anchor nw -bordermode ignore 
    place $top.but55 \
        -in $top -x 0 -relx 0.388 -y 0 -rely 0.732 -width 180 -relwidth 0 \
        -height 40 -relheight 0 -anchor nw -bordermode ignore 
    } ;# end vTcl:withBusyCursor 

    vTcl:FireEvent $base <<Ready>>
}

proc vTclWindow.top45 {base} {
    global vTcl
    if {$base == ""} {
        set base .top45
    }
    if {[winfo exists $base]} {
        wm deiconify $base; return
    }
    set top $base
    set target $base
    ###################
    # CREATING WIDGETS
    ###################
    vTcl::widgets::core::toplevel::createCmd $top -class Toplevel \
        -background #edf0f3 -highlightbackground $vTcl(actual_gui_bg) \
        -highlightcolor black 
    wm focusmodel $top passive
    wm geometry $top 582x798+788+406
    update
    # set in toplevel.wgt.
    global vTcl
    global img_list
    set vTcl(save,dflt,origin) 0
    wm maxsize $top 2564 1421
    wm minsize $top 120 1
    wm overrideredirect $top 0
    wm resizable $top 1 1
    wm deiconify $top
    set toptitle "GB2Fasta"
    wm title $top $toptitle
    namespace eval ::widgets::${top}::ClassOption {}
    set ::widgets::${top}::ClassOption(-toptitle) $toptitle
    vTcl:DefineAlias "$top" "gb2fasta" vTcl:Toplevel:WidgetProc "" 1
    set vTcl(real_top) {}
    vTcl:withBusyCursor {
    labelframe $top.lab58 \
        \
        -font {-family {Microsoft YaHei UI} -size 14 -weight normal -slant roman -underline 0 -overstrike 0} \
        -foreground $vTcl(actual_gui_fg) -text Input -background #edf0f3 \
        -height 189 -width 534 
    vTcl:DefineAlias "$top.lab58" "Labelframe1" vTcl:WidgetProc "gb2fasta" 1
    set site_3_0 $top.lab58
    ttk::label $site_3_0.tLa61 \
        -background #edf0f3 -foreground $vTcl(actual_gui_fg) \
        -font {-family {Microsoft YaHei UI} -size 12 -weight normal -slant roman -underline 0 -overstrike 0} \
        -relief flat -anchor w -justify left -text {Genbank file} \
        -compound left 
    vTcl:DefineAlias "$site_3_0.tLa61" "TLabel1" vTcl:WidgetProc "gb2fasta" 1
    ttk::entry $site_3_0.tEn62 \
        -font TkTextFont -foreground {} -background {} -takefocus {} \
        -cursor fleur 
    vTcl:DefineAlias "$site_3_0.tEn62" "gb_file" vTcl:WidgetProc "gb2fasta" 1
    ttk::style configure TButton -background $vTcl(actual_gui_bg)
    ttk::style configure TButton -foreground $vTcl(actual_gui_fg)
    ttk::style configure TButton -font "$vTcl(actual_gui_font_dft_desc)"
    ttk::button $site_3_0.tBu63 \
        -command open_file -takefocus {} -text Open -compound left 
    vTcl:DefineAlias "$site_3_0.tBu63" "open_gb" vTcl:WidgetProc "gb2fasta" 1
    ttk::separator $site_3_0.tSe65
    vTcl:DefineAlias "$site_3_0.tSe65" "TSeparator1" vTcl:WidgetProc "gb2fasta" 1
    ttk::label $site_3_0.tLa66 \
        -background #edf0f3 -foreground $vTcl(actual_gui_fg) \
        -font {-family {Microsoft YaHei UI} -size 12 -weight normal -slant roman -underline 0 -overstrike 0} \
        -relief flat -anchor w -justify left -text Gene -compound left 
    vTcl:DefineAlias "$site_3_0.tLa66" "TLabel1" vTcl:WidgetProc "gb2fasta" 1
    ttk::entry $site_3_0.tEn67 \
        -font TkTextFont -foreground {} -background {} -takefocus {} \
        -cursor fleur 
    vTcl:DefineAlias "$site_3_0.tEn67" "gb_file_1" vTcl:WidgetProc "gb2fasta" 1
    ttk::separator $site_3_0.tSe69 \
        -orient vertical 
    vTcl:DefineAlias "$site_3_0.tSe69" "TSeparator1" vTcl:WidgetProc "gb2fasta" 1
    place $site_3_0.tLa61 \
        -in $site_3_0 -x 0 -relx 0.056 -y 0 -rely 0.067 -width 0 \
        -relwidth 0.237 -height 0 -relheight 0.157 -anchor nw \
        -bordermode ignore 
    place $site_3_0.tEn62 \
        -in $site_3_0 -x 0 -relx 0.262 -y 0 -rely 0.1 -width 0 \
        -relwidth 0.561 -height 0 -relheight 0.1 -anchor nw \
        -bordermode ignore 
    place $site_3_0.tBu63 \
        -in $site_3_0 -x 0 -relx 0.835 -y 0 -rely 0.1 -width 80 -relwidth 0 \
        -height 30 -relheight 0 -anchor nw -bordermode ignore 
    place $site_3_0.tSe65 \
        -in $site_3_0 -x 0 -relx 0.093 -y 0 -rely 0.233 -width 0 \
        -relwidth 0.879 -height 0 -relheight 0.01 -anchor nw \
        -bordermode ignore 
    place $site_3_0.tLa66 \
        -in $site_3_0 -x 0 -relx 0.075 -y 0 -rely 0.267 -width 0 \
        -relwidth 0.093 -height 0 -relheight 0.157 -anchor nw \
        -bordermode ignore 
    place $site_3_0.tEn67 \
        -in $site_3_0 -x 0 -relx 0.187 -y 0 -rely 0.3 -width 180 -relwidth 0 \
        -height 30 -relheight 0 -anchor nw -bordermode ignore 
    place $site_3_0.tSe69 \
        -in $site_3_0 -x 0 -relx 0.561 -y 0 -rely 0.267 -width 0 \
        -relwidth 0.004 -height 0 -relheight 0.667 -anchor nw \
        -bordermode ignore 
    ###################
    # SETTING GEOMETRY
    ###################
    place $top.lab58 \
        -in $top -x 0 -relx 0.026 -y 0 -width 0 -relwidth 0.945 -height 0 \
        -relheight 0.376 -anchor nw -bordermode ignore 
    } ;# end vTcl:withBusyCursor 

    vTcl:FireEvent $base <<Ready>>
}

proc vTclWindow.top46 {base} {
    global vTcl
    if {$base == ""} {
        set base .top46
    }
    if {[winfo exists $base]} {
        wm deiconify $base; return
    }
    set top $base
    set target $base
    ###################
    # CREATING WIDGETS
    ###################
    vTcl::widgets::core::toplevel::createCmd $top -class Toplevel \
        -background #edf0f3 -highlightbackground $vTcl(actual_gui_bg) \
        -highlightcolor black 
    wm focusmodel $top passive
    wm geometry $top 800x601+533+822
    update
    # set in toplevel.wgt.
    global vTcl
    global img_list
    set vTcl(save,dflt,origin) 0
    wm maxsize $top 2564 1421
    wm minsize $top 120 1
    wm overrideredirect $top 0
    wm resizable $top 1 1
    wm deiconify $top
    set toptitle "Evaluate"
    wm title $top $toptitle
    namespace eval ::widgets::${top}::ClassOption {}
    set ::widgets::${top}::ClassOption(-toptitle) $toptitle
    vTcl:DefineAlias "$top" "evaluate" vTcl:Toplevel:WidgetProc "" 1
    set vTcl(real_top) {}
    vTcl:withBusyCursor {
    vTcl::widgets::ttk::scrolledwindow::CreateCmd $top.scr46 \
        -borderwidth 2 -relief groove -background $vTcl(actual_gui_bg) \
        -height 100 -highlightbackground $vTcl(actual_gui_bg) \
        -highlightcolor black -width 150 
    vTcl:DefineAlias "$top.scr46" "Scrolledwindow1" vTcl:WidgetProc "evaluate" 1

    $top.scr46.01 configure -background white \
        -borderwidth 2 \
        -height 75 \
        -highlightbackground #d9d9d9 \
        -highlightcolor black \
        -insertbackground black \
        -relief groove \
        -selectbackground #c4c4c4 \
        -selectforeground black \
        -width 125
    label $top.scr46.01.lab47 \
        -activebackground #f9f9f9 -activeforeground SystemButtonText \
        -anchor w -background $vTcl(actual_gui_bg) -compound left \
        -disabledforeground #a3a3a3 -font TkDefaultFont \
        -foreground $vTcl(actual_gui_fg) \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black \
        -text Label 
    vTcl:DefineAlias "$top.scr46.01.lab47" "Label1" vTcl:WidgetProc "evaluate" 1
    checkbutton $top.scr46.01.che48 \
        -activebackground $vTcl(analog_color_m) -activeforeground #000000 \
        -anchor w -background $vTcl(actual_gui_bg) -compound left \
        -disabledforeground #a3a3a3 -font TkDefaultFont \
        -foreground $vTcl(actual_gui_fg) \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black \
        -justify left -selectcolor #d9d9d9 -text Check -variable che48 
    vTcl:DefineAlias "$top.scr46.01.che48" "Checkbutton1" vTcl:WidgetProc "evaluate" 1
    place $top.scr46.01.lab47 \
        -in $top.scr46.01 -x 0 -relx 0.142 -y 0 -rely 0.102 -width 0 \
        -relwidth 0.053 -height 0 -relheight 0.059 -anchor nw \
        -bordermode ignore 
    place $top.scr46.01.che48 \
        -in $top.scr46.01 -x 0 -relx 0.156 -y 0 -rely 0.305 -width 0 \
        -relwidth 0.089 -height 0 -relheight 0.069 -anchor nw \
        -bordermode ignore 
    ###################
    # SETTING GEOMETRY
    ###################
    place $top.scr46 \
        -in $top -x 0 -relx 0.038 -y 0 -rely 0.083 -width 0 -relwidth 0.906 \
        -height 0 -relheight 0.662 -anchor nw -bordermode ignore 
    } ;# end vTcl:withBusyCursor 

    vTcl:FireEvent $base <<Ready>>
}

proc 36 {args} {return 1}


Window show .
set btop1 ""
if {$vTcl(borrow)} {
    set btop1 .bor[expr int([expr rand() * 100])]
    while {[lsearch $btop1 $vTcl(tops)] != -1} {
        set btop1 .bor[expr int([expr rand() * 100])]
    }
}
set vTcl(btop) $btop1
Window show .top44 $btop1
if {$vTcl(borrow)} {
    $btop1 configure -background plum
}
set btop2 ""
if {$vTcl(borrow)} {
    set btop2 .bor[expr int([expr rand() * 100])]
    while {[lsearch $btop2 $vTcl(tops)] != -1} {
        set btop2 .bor[expr int([expr rand() * 100])]
    }
}
set vTcl(btop) $btop2
Window show .top45 $btop2
if {$vTcl(borrow)} {
    $btop2 configure -background plum
}
set btop3 ""
if {$vTcl(borrow)} {
    set btop3 .bor[expr int([expr rand() * 100])]
    while {[lsearch $btop3 $vTcl(tops)] != -1} {
        set btop3 .bor[expr int([expr rand() * 100])]
    }
}
set vTcl(btop) $btop3
Window show .top46 $btop3
if {$vTcl(borrow)} {
    $btop3 configure -background plum
}

