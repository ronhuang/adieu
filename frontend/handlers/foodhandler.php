<?php

include_once '../constants.php';
include_once LIB_PATH.'util.php';
include_once LIB_PATH.'ui.php';

$fb = get_fb();

$title = $_REQUEST['title'];
$description = $_REQUEST['description'];
if (empty($description)) {
	$description = '';
}


if (empty($title)) {
	$result = array('result' => 'no_title');
}
else {
	$ch = curl_init();
	curl_setopt($ch, CURLOPT_URL, BACKEND_PATH.'item/create');
	curl_setopt($ch, CURLOPT_POST, 1);
	$data = 'title='.urlencode($title).'&description='.urlencode($description).'&uid='.$fb->get_loggedin_user();
	curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
	$result = curl_exec($ch);
	curl_close($ch);

	if (empty($result)) {
		$result = array('result' => 'failed',
						'title' => $title);
	}
	else {
		$result = json_decode($result, true);

		$food_key = ''.$result['key'];
	}
}


// Add the key to cookie
if ($food_key) {
	$json = $fb->api_client->data_getCookies($user, 'recent_food_keys');
	if ($json) {
		$recent_food_keys = json_decode($json, true);
	}
	else {
		$recent_food_keys = array();
	}

	if (empty($recent_food_keys[$food_key])) {
		array_unshift($recent_food_keys, $food_key);
	}

	$fb->api_client->data_setCookie($user, 'recent_food_keys', json_encode($recent_food_keys));
}


// Generate redirect URL
$canvas_url = $fb->get_facebook_url('apps') . '/' . APP_SUFFIX . 'newfood.php';
$first = true;
foreach ($result as $key => $value) {
	if ($first) {
		$canvas_url .= '?'.$key.'='.urlencode($value);
		$first = false;
	}
	else {
		$canvas_url .= '&'.$key.'='.urlencode($value);
	}
}


$fb->redirect($canvas_url);
