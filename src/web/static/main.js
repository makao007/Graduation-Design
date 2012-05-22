server_url = {
    'add_user': '/add_user',
    'del_user': '/del_user',
    'all_user': '/all_user',
    'add_cate': '/add_cate',
    'del_cate': '/del_cate',
    'edt_cate': '/edt_cate',
    'get_cate': '/get_cate',
    'login'   : '/login',
    'logout'  : '/logout',
    'islogin' : '/islogin',
    'relative': '/relative',
    'search':   '/search',                // below admin manage
    'is_admin': '/is_admin',
    'admin_login':'/admin_login',
    'is_admin_login' : '/admin_is_login',
    'update_admin_password': '/update_admin_password',
    'load_config' : '/config_qry',
    'save_config' : '/config_sav',
    'login_log' : '/login_log',
    'query_log' : '/query_log',
    'scrapy_log': '/scrapy_log'
}

function mul_line (s) {
    return s.replace(';', '\n');
}

function clear_div (id) {
    $(id).empty();
}

function clear_cate() {
    clear_div('#main_left_content');
}

function clear_value() {
    clear_div('#main_right_content');
}

function clear_input () {
    $('#edit_cate input').val('');
    $('#edit_cate textarea').val('');
}

function clear_cate_list () {
    clear_div('#manage_list');
}

//搜索，支持翻页
function search(opt) {
    var word = $('input#search_word').val().trim();
    var checkbox = $("#search input[type='checkbox']");
    var cb_title, cb_desc, cb_content, offset, num_page;
    cb_title = checkbox[0].checked ? 1 : 0;
    cb_desc  = checkbox[1].checked ? 1 : 0;
    cb_content = checkbox[2].checked ? 1 : 0;
    num_page = 15;
    $('#s_prev_search').attr('disabled',false);
    $('#s_next_search').attr('disabled',false);
    if (opt) {
        offset = (opt>0 ? 1 : -1) + parseInt($('#h_cur_search').val());
        if (offset < 0) {
            $('#s_prev_search').attr('disabled',true);
            return ;
        } else {
            if (offset==0)
                $('#s_prev_search').attr('disabled',true);
            $('#h_cur_search').val (offset);
        }
    } else {
        offset = 0;
        $('#h_cur_search').val (0);
        $('#s_prev_search').attr('disabled',true);
    }

    var path = server_url["search"] + "?" + encode_url ({"word": encodeURIComponent(word), "cb_title":cb_title, 'cb_desc':cb_desc, 'cb_content':cb_content, "offset": offset})+'&callback=?';
    if (word.length==0) {
        $('span#search_time').text('输出不能为空');
        return ;
    }

    $('span#search_time').text('正在查询...');
    $.getJSON(path, function (data) {
        $('input#search_word').val (data['word']);
        $('#search_content').empty();
        $('span#search_time').text('第'+(offset+1)+'页 有 ' + data['data'].length + '条结果  用时 ' + (''+data['time']).substr(0,4) + '秒');
        if (data['data'].length != num_page) {
            $('#s_next_search').attr('disabled', true);
        }

        load_record ($('#search_content'), data['data']);
    });
}

//左边栏目的显示
function load_cate (names) {
    clear_cate();
    clear_cate_list();
    var div = $('#main_left_content');
    $.each (names, function (index, value) {
            $('<li title="'+ value[3] + '" onclick=load_content(' + value[0] + ',' + index + '); >' + value[1] + '</li>').appendTo(div);
    });
}

//加载用户关注的内容
function load_record (div, data) {
    $.each (data, function (index, value) {
        var ul = $('<ul/>');
        $('<li/>').addClass('item1').text(index+1).appendTo(ul);
        $('<li/>').addClass('item2').text(value[0]).appendTo(ul);
        $('<li/>').html('<a target="_blank" href="' + value[3] + '" title="' + value[2] + '">' + value[1] + '</a>').addClass('item3').appendTo(ul);
        div.append(ul);
    });
}

//查询的主要界面
function load_content (id,tmp) {
    clear_value();
    var contents = mydata.data[id];
    var div = $('#main_right_content');
    $('#h_cur_page').val (0);
    $('#h_focus_id').val (id);
    $('#s_cur_page').text('');
    $('#s_next_page').attr('disabled',false);
    $('#s_prev_page').attr('disabled',true);
    load_record (div, contents);

    var div = $('#main_left_content li');
    div.css ('background','white');
    $(div[tmp]).css('background','#f3f3f3');
}

//翻页查询
function relative_page (opt) {
    var page = parseInt($('#h_cur_page').val()) + parseInt(opt);
    var fid  = $('#h_focus_id').val();
    if ( page < 0 || !fid) {
        return ;
    } else {
        clear_value();

        $('#h_cur_page').val(page);
        var url = server_url["relative"] + "?" + encode_url({"fid":fid, "offset": page})+"&callback=?";
        $('#s_cur_page').text('正在查询...');
        $.getJSON(url, {}, function (data) {
            clear_value();

            $( (opt>0 ? '#s_prev_page':'#s_next_page')).attr('disabled',false);
            if (data[fid].length < 15) {
                $('#s_next_page').attr('disabled',true);
            } else if (page == 0) {
                $('#s_prev_page').attr('disabled',true);
            }

            load_record ($('#main_right_content'), data[fid]);
            $('#s_cur_page').text('第 ' + (page+1) + '页  共' + data[fid].length + ' 条记录');
        });
    }
}


//显示管理条目
function edit_cate (id) {

    if (id<0 || id>= mydata.name_info.length) {
        var data = ['','','','',''];
        var title= '添加条目';
        clear_input();
    }
    else {
        var data = mydata.name_info[id];
        var title= '编辑条目';
    }
    $('#edit_cate div:first').text (title);
    $('#edit_cate input:first').val(data[0]);
    $('#edit_cate input:eq(1)').val(data[1]);
    $('#edit_cate textarea:first').val(mul_line(data[3]));
    $('#edit_cate textarea:eq(1)').val(mul_line(data[2]));

    display_block('#edit_cate');
}


//删除一条目
function del_cate (id) {
    display_block ('#del_cate');
    $('#del_cate span:first').click( function () {
        $.get(server_url.del_cate+'?id='+id,{}, function (data) {
            hide_block('#del_cate');
            var tmp = $.parseJSON(data);
            if (tmp.status) {
                display_msg ("删除成功");
                reload_data();
            } else {
                display_msg (tmp.text);
            }
        });
    });
}

//还原，隐藏半透明
function hide_block (id) {
    $(id).hide();
    $('#background').hide();
}

//显示一条消息，动画从上向下显示， 4秒后自动隐藏
function display_msg (msg) {
    var obj = $('#message');
    obj.hide();
    var date = new Date();
    var time = date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds() + '<br/>';
    obj.html(time + msg);
    var width = ($(document).width() - obj.width())/2;
    var width = ($(document).width() - 100)/2;
    obj.css('left', width + '.px');
    obj.slideDown(800);
    setTimeout (function () { obj.slideUp(800); }, 4000);
}

//将背景设为半透明，再显示一个块
function display_block (id) {
    var bg = $('#background');
    bg.width  ( $(document).width());
    bg.height ( $(document).height());
    bg.show();
    bg.fadeTo('fast',0.7);
    $(id).css ('top','160px');
    $(id).css ('left', ($(document).width() - $(id).width())/2+'.px');
    $(id).show();
}

//条目的管理
function load_manage (data) {
    var div = $("#manage_list");
    $.each (data, function (index, value ) {
            var ul = $("<ul/>");
            $('<li/>').text (index+1).addClass('ctem0').appendTo(ul);
            $('<li/>').text (value[1]).addClass('ctem1').appendTo(ul);
            $('<li/>').text (value[3]).addClass('ctem2').appendTo(ul);
            $('<li/>').text (value[2]).addClass('ctem3').appendTo(ul);
            $('<li/>').html('<a href="javascript:void(0);" onclick="edit_cate(' + index + ')">编辑</a>').addClass('ctem4').appendTo(ul);
            $('<li/>').html('<a href="javascript:void(0);" onclick="del_cate(' + value[0] + ')">删除</a>').addClass('ctem5').appendTo(ul);

            div.append (ul);
            });
}

// 注销退出
function logout () {
    $.get (server_url.logout,{},function(data){ location.reload(); });
}

// 用户登录与管理员登录共用
function login_base (block_id, url, call_back1, call_back2 ) {
    var input = $('#' + block_id + ' input');
    var user  = input[0].value;
    var pawd  = input[1].value;
    if (user=='用户名' || pawd=='密码') {
        display_msg ('用户名和密码不能为空');
        return;
    }
    if (user.length > 0 && pawd.length > 0) {
        var parm = encode_url ({'username':user, 'password': pawd});
        var url  = url + '?' + parm;
        $.get (url, {}, function (data1) {
            console.log(data1);
            var tmp = $.parseJSON(data1);                                     
            if (tmp && tmp.status == 1) {
                $('#' + block_id).hide();
                call_back1(tmp);   // login succ
            } else {
                call_back2(tmp);  // login fail
            }
        });
    } else {
        display_msg ('用户名和密码不能为空');
    }
}

//用户登录
function login () {
    login_base ('login', server_url.login, function (tmp){
            $('#nav ul li:first').html('您好：' + tmp.text); 
            $('#nav ul li:first').attr('onclick',''); 
            $('#login').hide(); get_category_info(); 
        }, function(tmp){
            console.log(tmp);
            if (tmp)
                 display_msg(tmp.text);
            ;} 
        );
}

//添加一个关注条目
function add_cate () {
    var add_cate = $('#edit_cate');
    var id       = add_cate.find('input')[0].value;
    var title    = add_cate.find('input')[1].value;
    var keys     = encodeURIComponent(add_cate.find('textarea')[0].value);
    var sources  = encodeURIComponent(add_cate.find('textarea')[1].value);
    if (title.length==0) {
        display_msg ("条目名称不能为空");
        return ;
    }
    if (keys.length==0) {
        display_msg ("关键词不能空");
        return ;
    }
    if (sources.length==0) {
        display_msg ("来源不能空");
        return ;
    }
    
    var parm = encode_url( {'id':id, 'title':title, 'keys':keys, 'sources':sources } );
    var url  = server_url.add_cate + '?' + parm;
    $.get (url, {} , function (data) {
        var tmp = $.parseJSON(data); 
        if (tmp.status==0) {
            display_msg ("操作出错   " + tmp.text );
        } else {
            hide_block('#edit_cate'); 
            display_msg("操作成功   " + tmp.text );
            reload_data();
        }
    });
}

//注册一个用户
function add_user () {
    var input = $('#register input');
    var user  = input[0].value;
    var pawd1 = input[1].value;
    var pawd2 = input[2].value;
    if (user.length == 0) {
        display_msg ('用户名不能为空');
        return ;
    }
    if (pawd1.length == 0) {
        display_msg ('密码不能为空');
        return ;
    }
    if (pawd1 != pawd2) {
        display_msg ('两次输入的密码不一致');
        return ;
    }
    var parm  = encode_url ({'user': user, 'pawd1':pawd1 });
    var url   = server_url.add_user + '?' + parm;
    $.get(url,{}, function (data) {
        var tmp = $.parseJSON(data);
        if (tmp.status) {
            display_msg ("成功注册用户");
            hide_block ('#register'); 
        } else {
            display_msg(tmp.text);
        }
    });
}

// 将一个字典转为URL参数形式的字符串
function encode_url (d) {
    var result = '';
    for (var i in d) {
        result = result + i + '=' + d[i] + '&';
    }
    if (result.length > 0)
        result = result.substr(0, result.length-1);
    return result;
}

//
function reload_data () {
    mydata = {'name_info':[], 'data':[]};
    reflash_data ();
    get_category_info();
}

function reflash_data () {
    load_cate(mydata.name_info); 
    load_manage(mydata.name_info);
}

//取得相关信息
function get_category_info () {
    jQuery.getJSON('categorys?callback=?',function (data) {
        mydata = data;
        reflash_data();
        jQuery.getJSON(server_url['relative'] + '?callback=?', function (data) {
           mydata['data'] = data;
        }); 
    });
}

//判断是否已登录
function islogin() {
    $.get(server_url.islogin,{}, function (data) {
        var tmp = $.parseJSON(data);
        if (tmp && tmp.status == 1) {
            $('#login').hide();
            $('#nav ul li:first').html('您好：' + tmp.text);
            get_category_info();
        } else {
            $('#nav ul li:first').html('首页');
        }
    });
}


function load_statics (id) {
    $('div#statics_right>div').hide();
    $('div#statics_'+id).show();

    $('#statics div ul li').css ('background','white');
    $('#statics div ul li:eq(' + (id-1) + ')').css ('background','#f3f3f3');
    if (id==6){
        $("#statics_6 input[type='password']").val('');
    } else if (id==5) {
        load_config ();
    } else if (id==4) {
        login_log ();
    } else if (id==2) {
        query_log ();
    } else if (id==1) {
        list_all_user();
    } else if (id==3) {
        scrapy_log ();
    }
}

//管理员退出
function admin_logout () {
    location.href = "/admin_logout";
}


function admin_load (tmp) {
    $('#statics').show();
    $('#admin_login').hide();
}

function is_admin () {
    $.get(server_url.is_admin_login,{}, function (data) {
        var tmp = $.parseJSON(data);
        if (tmp.status == 1) {
            admin_load(tmp);
            // load data
        }else {
        }
    });
}

//管理员登录
function admin_login () {
    login_base ('admin_login', server_url.admin_login, function (tmp) {admin_load (tmp);}, function (tmp) {display_msg("用户名或密码错误"); });
}

//管理员修改密码
function update_password() {
    var input = $('#statics_6 input');
    var old_pawd  = input[0].value.trim();
    var new_pawd1 = input[1].value.trim();
    var new_pawd2 = input[2].value.trim();
    if (old_pawd && new_pawd1 && new_pawd2) {
        if (new_pawd1 == new_pawd2) {
            var url = server_url.update_admin_password + '?' + encode_url ({'password0':old_pawd,'password1':new_pawd1}) ;
            $.get(url, {}, function (data) {
                var result = jQuery.parseJSON(data);
                if (result.status==1 ) {
                    display_msg ("修改密码成功");
                } else {
                    display_msg ("修改密码失败");
                } });
        } else {
            display_msg ("两次输入的新密码不一致");
        }
    } else {
        display_msg ("密码不能为空");
    }
}

//加载配置信息
function load_config () {
    fetch_config_data(server_url['load_config']);
}

function load_config_info(data){
    var input = $('#statics_5 input');
    input[0].value = data['max_page'];
    input[1].value = data['max_deep'];
    input[2].value = data['scy_wait'];
    input[3].value = data['scy_stop'];
    input[4].value = data['keep_time'];
    input[5].value = data['search_num'];
    input[6].value = data['keyword_num'];
}

//保存配置信息
function save_config_info (data) {
    var input = $('#statics_5 input');
    var data = {};
    data['max_page'] = input[0].value;
    data['max_deep'] = input[1].value;
    data['scy_wait'] = input[2].value;
    data['scy_stop'] = input[3].value;
    data['keep_time'] = input[4].value;
    data['search_num']  = input[5].value;
    data['keyword_num'] = input[6].value;

    var url = server_url['save_config'] + '?' + encode_url(data);
    fetch_config_data (url);
    display_msg ('操作修改配置成功');
}

function fetch_config_data(url) { 
    $.get(url, {} , function (text) {
        var result = $.parseJSON(text);
        if (result.status == 1) {
            if (result.text){
                var config_data = $.parseJSON(decodeURIComponent(result.text))
                load_config_info (config_data);
                //load_config_info(config_data);
            }
        } else {
            display_msg ("操作失败");
        }
    });
}

function login_log () {
    var url = server_url.login_log;
    $.getJSON(url, function (data) {
        var table = $('#statics_4 table:first');
        table.empty();
        $("<tr><th>序号</th><th>时间</th><th>用户名</th><th>操作</th></tr>").appendTo(table);
        $.each (data, function (index,item) {
            var s = "<tr><th>" + (index+1) + "</th><th>" + item[0] + "</th><th>" + item[2] + "</th><th> " + (item[3]==1 ? "登录":"注销" ) + "</th></tr>";
            $(s).appendTo(table);
        });
    });
}
function query_log () {
    var url = server_url.query_log;
    $.getJSON(url, function (data) {
        var tables = $('#statics_2 table');
        $.each (tables, function (inde, table) {
            table = $(table);
            table.empty();
            $("<tr><th class='ttem1'>排行</th><th class='ttem2'>关键词</th><th class='ttem3'>查询次数</th></tr>").appendTo(table);
            $.each (data[inde], function (index,item) {
                var s = "<tr><th class='ttem1'>" + (index+1) + "</th><th><div class='ttem2'>" + item[1] + "</div></th><th class='ttem3'>" + item[0] + "</th><th>"; 
                $(s).appendTo(table);
            });
        });
    });
}

function list_all_user () {
    var url = server_url.all_user;
    $.getJSON(url, function (data) {
        var table = $('#statics_1 table:first');
        table.empty();
        $("<tr><th>序号</th><th>注册时间</th><th>用户名</th><th>删除?</th>").appendTo(table);
        $.each (data, function (index,item) {
            var s = "<tr><th>" + (index+1) + "</th><th>" + item[2] + "</th><th>" + item[1] + "</th><th> " + "<input type='button' value='删除' class='button' onclick=del_user('" + item[0] + "','#del_user',list_all_user)></th></tr>";
            $(s).appendTo(table);
        });
    });
}

function del_user (id,block_id,cbk) {
    var url = server_url.del_user;
    display_block (block_id);
    $(block_id + ' span:first').click( function () {
        $.get(url+'?id='+id,{}, function (data) {
            hide_block(block_id);
            var tmp = $.parseJSON(data);
            if (tmp.status) {
                display_msg ("删除成功");
                cbk();
            } else {
                display_msg (tmp.text);
            }
        });
    });
    $(block_id + " span:eq(1)").click ( function () {
        hide_block (block_id);
    });
}

function scrapy_log () {
    var url = server_url.scrapy_log;
    $.getJSON(url, function (data) {
        var table = $('#statics_3 table:first');
        table.empty();
        $("<tr><th>序号</th><th>开始时间</th><th>结束时间</th><th>最大深度</th><th>最大页数</th><th>下载数</th></tr>").appendTo (table);
        $.each (data, function (index, item) {
            var tmp = "<tr><td>" + (index+1) + "</td><td>"+item.start_time+"</td><td>"+item.end_time+"</td><td>" + item.max_deep + "</td><td>" + item.max_page + "</td><td>" + item.visited_len + "</td></tr>" ;
            $(tmp).appendTo(table);
        });
    });
}

function setCookie(name,value)//两个参数，一个是cookie的名子，一个是值
{
    var Days = 1; //此 cookie 将被保存 1 天
    var exp  = new Date();    //new Date("December 31, 9998");
    exp.setTime(exp.getTime() + Days*24*60*60*1000);
    document.cookie = name + "="+ escape (value) + ";expires=" + exp.toGMTString();
}
function getCookie(name)//取cookies函数
{
    var arr = document.cookie.match(new RegExp("(^| )"+name+"=([^;]*)(;|$)"));
    if(arr != null) return unescape(arr[2]); return null;

}
function delCookie(name)//删除cookie
{
    var exp = new Date();
    exp.setTime(exp.getTime() - 1);
    var cval=getCookie(name);
    if(cval!=null) document.cookie= name + "="+cval+";expires="+exp.toGMTString();
}

function top_menu(div) {
    var s = "body>div#nav~div[id!='"+div+"']";
    console.log(s);
    $(s).hide();
    $('#'+div).show();
    if (div=='login') 
        $('#aboutme').show();
}
