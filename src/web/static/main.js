server_url = {
    'add_user': '/add_user',
    'del_user': '/del_user',
    'add_cate': '/add_cate',
    'del_cate': '/del_cate',
    'edt_cate': '/edt_cate',
    'get_cate': '/get_cate',
    'login'   : '/login',
    'logout'  : '/logout',
    'islogin' : '/islogin'
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

//左边栏目的显示
function load_cate (names) {
    var div = $('#main_left_content');
    $.each (names, function (index, value) {
            $('<li onclick=load_content(' + index + '); >' + value + '</li>').appendTo(div);
            });
}

//查询的主要界面
function load_content (id) {
    clear_value();
    var contents = mydata.data[id];
    var div = $('#main_right_content');
    $.each (contents, function (index, value) {
            var ul = $('<ul/>');
            for (var i=0;i<value.length;i++) {
                if (i==3) {
                    $('<li/>').html('<a target="_blank" href="' + value[i] + '">' + value[i] + '</a>').addClass('item'+(1+i)).appendTo(ul);
                }
                else {    
                    $('<li/>').text(value[i]).addClass('item'+(1+i)).appendTo(ul);
                }
            }
            div.append(ul);
            });
}

//显示管理条目
function edit_cate (id) {

    if (id<0 || id>= mydata.name_info.length) {
        var data = ['','','','',''];
        var title= '添加条目';
    }
    else {
        var data = mydata.name_info[id];
        var title= '编辑条目';
    }
    $('#edit_cate div:first').text (title);
    $('#edit_cate input:first').value = data[0];
    $('#edit_cate input').get(1).value = data[1];
    $('#edit_cate textarea:first').text (mul_line(data[2]));
    $('#edit_cate textarea').get(1).value = (mul_line(data[3]));

    display_block('#edit_cate');
}

//删除一条目
function del_cate (id) {
    display_block ('#del_cate');
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
            $('<li/>').text (index).addClass('ctem0').appendTo(ul);
            $('<li/>').text (value[1]).addClass('ctem1').appendTo(ul);
            $('<li/>').text (value[2]).addClass('ctem2').appendTo(ul);
            $('<li/>').text (value[3]).addClass('ctem3').appendTo(ul);
            $('<li/>').html('<a href="javascript:void(0);" onclick="edit_cate(' + index + ')">编辑</a>').addClass('ctem4').appendTo(ul);
            $('<li/>').html('<a href="javascript:void(0);" onclick="del_cate(' + index + ')">删除</a>').addClass('ctem5').appendTo(ul);

            div.append (ul);
            });
}

// 加载条目信息
function load_data(data) {
    load_cate(data);
}

// ajax从服务器获取信息
function get_data () {
    var url = '/';
    $.get(url,{}, load_data);
}

function logout () {
    $.get (server_url.logout,{},function(data){ location.reload(); });
}

function login () {
    var input = $('#login input');
    var user  = input[0].value.trim();
    var pawd  = input[1].value.trim();
    if (user=='用户名' || pawd=='密码') {
        display_msg ('用户名和密码不能为空');
        return;
    }
    if (user.length > 0 && pawd.length > 0) {
        var parm = encode_url ({'username':user, 'password': pawd});
        var url  = server_url.login + '?' + parm;
        $.get (url, {}, function (data) {
            console.log (data);
            var tmp = $.parseJSON(data);
            if (tmp.status == 0) {
                display_msg (tmp.text);
            } else {
                $('#nav ul li:first').html('您好：' + tmp.text);
                $('#login').hide();
            }
        });
    } else {
        display_msg ('用户名和密码不能为空');
    }
}

function add_cate () {
    var add_cate = $('#edit_cate');
    var id       = add_cate.find('input')[0].value.trim();
    var title    = add_cate.find('input')[1].value.trim();
    var keys     = add_cate.find('textarea')[0].value.trim();
    var sources  =  encodeURIComponent(add_cate.find('textarea')[1].value.trim());
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
    $.get (url, {} , function (data) {console.log(data);});
}

function add_user () {
    var input = $('#register input');
    var user  = input[0].value.trim();
    var pawd1 = input[1].value.trim();
    var pawd2 = input[2].value.trim();
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
    var i;
    var result = '';
    for (i in d) {
        result = result + i.trim() + '=' + d[i] + '&';
    }
    if (result.length > 0)
        result = result.substr(0, result.length-1);
    return result;
}

function islogin() {
    $.get(server_url.islogin,{}, function (data) {
        var tmp = $.parseJSON(data);
        if (tmp.status == 1) {
            $('#login').hide();
            $('#nav ul li:first').html('您好：' + tmp.text);
        } else {
            $('#nav ul li:first').html('首页');
        }
    });
}

$(document).ready( function () { 
    load_data(mydata.names); 
    $('#main').hide(); 
    $('#manage').hide();
    load_manage(mydata.name_info);
    islogin();
    });

