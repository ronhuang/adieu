<?php

include_once '../constants.php';
include_once LIB_PATH.'util.php';


function render_header($selected ='Home') {
	$ts = filemtime(CSS_PATH.'page.css');
	$header = '<link rel="stylesheet" type="text/css" href="'.ROOT_LOCATION.'/css/page.css?ts='.$ts.'" />';
	$ts = filemtime(JS_PATH.'base.js');
	$header .= '<script src="'.ROOT_LOCATION.'/js/base.js?ts='.$ts.'" ></script>';

	$header .= '<fb:dashboard/>';

	$header .=
		'<fb:tabs>'
		.'<fb:tab-item title="Home" href="index.php" selected="' . ($selected == 'Home') .'" />'
		.'<fb:tab-item title="New Food" href="newfood.php" selected="' . ($selected == 'New') . '" />'
		.'<fb:tab-item title="Vote Food" href="votefood.php" selected="' . ($selected == 'Vote') . '" />'
		.'</fb:tabs>';
	$header .= '<div id="main_body">';
	return $header;
}

function render_footer() {
	$footer = '</div>';
	return $footer;
}

function render_food($type) {
	$foods = array(
		array('玉米', 0 ,0)
		,array('牛排', 0 ,0)
		,array('培根', 0 ,0)
		,array('啤酒', 0 ,0)
		,array('澎糖', 0 ,0)
		,array('木炭', 0 ,0)
		);

	$ret = '';
	$i = 0;
	$ret .= '<div class="table">';

	foreach($foods as $food) {
		list($title, $uid, $vote) = $food;
		$ret .= '<div onclick="select('.$i.')" onmouseover="over('.$i.')" onmouseout="out('.$i.')" class="box" id="food_'.$i.'">'
			.'<div class="title">'.$title.'</div>'
			.'</div>';
		$i++;
	}
	$ret .= '</div>';

	return $ret;
}

function render_feedback_message($result, $title) {
	$ret = '<div style="overflow: hidden" id="feedback_message">';

	if ($result == 'added') {
		$ret .= '<fb:success>';
		$ret .= '<fb:message>成功</fb:message>';
		$ret .= '已將'.$title.'加入清單';
		$ret .= '</fb:success>';
	}
	elseif ($result == 'duplicated') {
		$ret .= '<fb:error>';
		$ret .= '<fb:message>重複</fb:message>';
		$ret .= ''.$title.'已在清單中';
		$ret .= '</fb:error>';
	}
	elseif ($result == 'no_title') {
		$ret .= '<fb:error>';
		$ret .= '<fb:message>錯誤</fb:message>';
		$ret .= '請輸入名稱';
		$ret .= '</fb:error>';
	}
	elseif ($result == 'not_implemented') {
		$ret .= '<fb:error>';
		$ret .= '<fb:message>錯誤</fb:message>';
		$ret .= '此功能尚未實做';
		$ret .= '</fb:error>';
	}
	elseif ($result == 'failed' && !empty($title)) {
		$ret .= '<fb:error>';
		$ret .= '<fb:message>錯誤</fb:message>';
		$ret .= '無法將'.$title.'加入清單';
		$ret .= '</fb:error>';
	}
	elseif (!empty($result)) {
		$ret .= '<fb:error message="錯誤"/>';
	}

	$ret .= '</div>';


	$ret .= '<script type="text/javascript">';
	$ret .= 'Animation(document.getElementById("feedback_message")).duration(2000).checkpoint().to("height", "0px").to("opacity", 0).hide().go();';
	$ret .= '</script>';


	return $ret;
}

function render_popular_foods($user, $count, $with_comment) {
	$ret = retrieve_foods('popular');
	if ($ret['result'] != 'success') {
		$foods = array();
	}
	else {
		$foods = $ret['foods'];
	}

	$ret = '<fb:wall>';
	$i = 0;
	foreach ($foods as $food) {
		$ret .= '<fb:wallpost uid="'.$food['owner'].'" t="'.$food['date'].'">';
		$ret .= '<p>'.$food['title'].'</p>';
		$ret .= '<p>'.$food['description'].'</p>';
		$ret .= '<p>目前得票數是 <span id="votes_'.$i.'">'.$food['votes'].'</span></p>';

		$ret .= '<form id="form_'.$i.'">';
		$ret .= '<input type="hidden" name="key" value="'.$food['key'].'"/>';
		$ret .= '<input type="hidden" name="owner" value="'.$user.'"/>';
		$ret .= '<input type="hidden" name="cur_votes" value="'.$food['votes'].'"/>';
		$ret .= '</form>';
		$ret .= '<a clickrewriteurl="'.BACKEND_PATH.'vote/create'.'" clickrewriteform="form_'.$i.'" clickrewriteid="votes_'.$i.'">推薦</a>';
		$ret .= '</fb:wallpost>';

		$i++;

		if ($count && $count > 0 && $i >= $count) {
			break;
		}
	}
	$ret .= '</fb:wall>';

	return $ret;
}

/*
function render_recent_food($food_keys, $user) {
	$ret = '';
	$i = 0;

	foreach ($food_keys as $food_key) {
		$ret = retrieve_food($food_key);
		if ($ret['result'] != 'success') {
			continue;
		}

		$food = $ret['food'];

		echo '<fb:wallpost uid="'.$user.'">';
		echo '<p>'$food['title']'</p>';
		echo '<p>'$food['description']'</p>';
		echo '</fb:wallpost>';

		$i++;
		if ($i >= 5) {
			break;
		}
	}

	if (!empty($ret)) {
		$ret = '<h2>最近妳/你加入</h2><fb:wall>'.$ret;
		$ret .= '</fb:wall>';
	}

	return $ret;
}
*/
