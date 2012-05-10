server_url = {
    'add_user': '/add_user',
    'del_user': '/del_user',
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
    'update_admin_password': '/update_admin_password'
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

function search() {
    var word = $('input#search_word').val().trim();
    var path = server_url["search"] + "?" + encode_url ({"word": encodeURIComponent(word)})+'&callback=?';
    if (word.length==0) {
        $('span#search_time').text('输出不能为空');
    }

    $('span#search_time').empty();
    $.getJSON(path, function (data) {
        $('input#search_word').val (data['word']);
        $('#search_content').empty();
        $('span#search_time').text('共有 ' + data['data'].length + '条记录;  用时 ' + data['time']);

        load_record ($('#search_content'), data['data']);
    });
}

//左边栏目的显示
function load_cate (names) {
    clear_cate();
    clear_cate_list();
    var div = $('#main_left_content');
    $.each (names, function (index, value) {
            $('<li title="'+ value[3] + '" onclick=load_content(' + value[0] + '); >' + value[1] + '</li>').appendTo(div);
    });
}

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
function load_content (id) {
    clear_value();
    var contents = mydata.data[id];
    var div = $('#main_right_content');
    load_record (div, contents);
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

function display_msg (msg) {
    var obj = $('#message');
    obj.hide();
    var date = new Date();
    var time = date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds() + '<br/>';
    obj.html(time + msg);
    var width = ($(document).width() - obj.width())/2;
    obj.css('left', width + '.px');
    obj.slideDown(800);
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


function logout () {
    $.get (server_url.logout,{},function(data){ location.reload(); });
}

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
        $.get (url, {}, function (data) {
            var tmp = $.parseJSON(data);                                     
            if (tmp.status == 1) {
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

function login () {
    login_base ('login', server_url.login, function (tmp){
            $('#nav ul li:first').html('您好：' + tmp.text); 
            $('#nav ul li:first').attr('onclick',''); 
            $('#login').hide(); get_category_info(); 
        }, function(tmp){display_msg (tmp.text);} );
}

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
    $.get(url,{}, function (data) {display_msg(data);});
}

function encode_url (d) {
    var result = '';
    for (var i in d) {
        result = result + i + '=' + d[i] + '&';
    }
    if (result.length > 0)
        result = result.substr(0, result.length-1);
    return result;
}

function reload_data () {
    mydata = {'name_info':[], 'data':[]};
    reflash_data ();
    get_category_info();
}

function reflash_data () {
    load_cate(mydata.name_info); 
    load_manage(mydata.name_info);
}


function get_category_info () {
    jQuery.getJSON('categorys?callback=?',function (data) {
        mydata = data;
        reflash_data();
        jQuery.getJSON(server_url['relative'] + '?callback=?', function (data) {
           mydata['data'] = data;
        }); 
    });
}

function islogin() {
    $.get(server_url.islogin,{}, function (data) {
        var tmp = $.parseJSON(data);
        if (tmp.status == 1) {
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
}

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
        } });
}

function admin_login () {
    login_base ('admin_login', server_url.admin_login, function (tmp) {console.log(tmp); admin_load (tmp);}, function (tmp) {console.log(tmp); });
}

function update_password() {
    var input = $('#statics_6 input');
    var old_pawd  = input[0].value.trim();
    var new_pawd1 = input[1].value.trim();
    var new_pawd2 = input[2].value.trim();
    if (old_pawd && new_pawd1 && new_pawd2) {
        if (new_pawd1 == new_pawd2) {
            var url = server_url.update_admin_password + '?' + encode_url ({'password0':old_pawd,'password1':new_pawd1}) ;
            console.log (url);
            $.get(url, {}, function (data) {
                if (data.status ) {
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
