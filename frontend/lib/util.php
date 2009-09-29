<?php
error_log(CLIENT_PATH);
include_once CLIENT_PATH.'facebook.php';

function get_fb() {
	return new Facebook(API_KEY, SECRET_KEY);
}

function retrieve_food($food_key) {
	$ch = curl_init();
	curl_setopt($ch, CURLOPT_URL, BACKEND_PATH.'item/show/'.$food_key);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
	$json = curl_exec($ch);
	curl_close($ch);

	if (empty($json)) {
		$result = array('result' => 'not_exist',
						'food_key' => $food_key);
	}
	else {
		$result = json_decode($json, true);
	}

	return $result;
}

function cmp_popular($a, $b) {
	$va = (int)$a['votes'];
	$vb = (int)$b['votes'];
	if ($va == $vb) {
		return 0;
	}
	return ($va < $vb) ? 1 : -1;
}

function retrieve_foods($group) {
	$ch = curl_init();
	curl_setopt($ch, CURLOPT_URL, BACKEND_PATH.'item/list');
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
	$json = curl_exec($ch);
	curl_close($ch);

	if (empty($json)) {
		$result = array('result' => 'failed',
						'group' => $group);
	}
	else {
		$result = json_decode($json, true);

		if ($group == 'popular') {
			usort($result['foods'], 'cmp_popular');
		}
	}

	return $result;
}
