# -*- coding: utf-8 -*-

media_xml_start = '\
<?xml version="1.0" encoding="UTF-8"?>\
\n<includes>\
\n    <include name="{main_include}">'

media_xml_end = '\
\n    </include>\
\n</includes>'

media_xml_body = '\
\n        <include content="{cpath_type}">\
\n            <param name="content_path" value="{cpath_path}"/>\
\n            <param name="widget_header" value="{cpath_header}"/>\
\n            <param name="widget_target" value="videos"/>\
\n            <param name="list_id" value="{cpath_list_id}"/>\
\n        </include>'


category_top_xml = '\
<?xml version="1.0" encoding="UTF-8"?>\
\n<includes>\
\n    <include name="{main_include}">\
\n        <include content="WidgetListCategories">\
\n            <param name="content_path" value="{cpath_path}"/>\
\n            <param name="widget_header" value="{cpath_header}"/>\
\n            <param name="widget_target" value="videos"/>\
\n            <param name="list_id" value="{cpath_list_id}"/>\
\n        </include>\
\n    </include>\
\n</includes>'

category_bottom_xml = '\
<?xml version="1.0" encoding="UTF-8"?>\
\n<includes>\
\n    <include name="{main_include}">\
\n        <include content="WidgetListCategories">\
\n            <param name="content_path" value="{cpath_path}"/>\
\n            <param name="widget_header" value="{cpath_header}"/>\
\n            <param name="widget_target" value="videos"/>\
\n            <param name="list_id" value="{cpath_list_id}"/>\
\n        </include>\
\n    </include>\
\n</includes>'

main_menu_movies_xml = '\
<?xml version="1.0" encoding="UTF-8"?>\
\n<includes>\
\n    <include name="MoviesMainMenu">\
\n        <item>\
\n            <label>$LOCALIZE[342]</label>\
\n            <onclick>ActivateWindow(Videos,{main_menu_path},return)</onclick>\
\n            <property name="menu_id">$NUMBER[19000]</property>\
\n            <thumb>icons/sidemenu/movies.png</thumb>\
\n            <property name="id">movies</property>\
\n            <visible>!Skin.HasSetting(HomeMenuNoMovieButton)</visible>\
\n        </item>\
\n    </include>\
\n</includes>'

main_menu_tvshows_xml = '\
<?xml version="1.0" encoding="UTF-8"?>\
\n<includes>\
\n    <include name="TVShowsMainMenu">\
\n        <item>\
\n            <label>$LOCALIZE[20343]</label>\
\n            <onclick>ActivateWindow(Videos,{main_menu_path},return)</onclick>\
\n            <property name="menu_id">$NUMBER[22000]</property>\
\n            <thumb>icons/sidemenu/tv.png</thumb>\
\n            <property name="id">tvshows</property>\
\n            <visible>!Skin.HasSetting(HomeMenuNoTVShowButton)</visible>\
\n        </item>\
\n    </include>\
\n</includes>'

default_widget = '\
<?xml version="1.0" encoding="UTF-8"?>\
\n<includes>\
\n    <include name="{includes_type}">\
\n    </include>\
\n</includes>'

default_category_top_widget = '\
<?xml version="1.0" encoding="UTF-8"?>\
\n<includes>\
\n    <include name="{includes_type}">\
\n    </include>\
\n</includes>'

default_category_bottom_widget = '\
<?xml version="1.0" encoding="UTF-8"?>\
\n<includes>\
\n    <include name="{includes_type}">\
\n    </include>\
\n</includes>'

default_main_menu = '\
<?xml version="1.0" encoding="UTF-8"?>\
\n<includes>\
\n    <include name="{includes_type}">\
\n    </include>\
\n</includes>'



