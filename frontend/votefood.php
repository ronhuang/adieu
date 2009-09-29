<?php

include_once 'constants.php';
include_once LIB_PATH.'util.php';
include_once LIB_PATH.'ui.php';

$fb = get_fb();
$user = $fb->require_login();


echo render_header('Vote');

echo render_feedback_message($_REQUEST['result'], $_REQUEST['title']);


echo '<h2>推薦</h2>';


echo render_popular_foods($user);

echo render_footer();
