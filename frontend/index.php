<?php

include_once 'constants.php';
include_once LIB_PATH.'util.php';
include_once LIB_PATH.'ui.php';

$fb = get_fb();
$user = $fb->require_login();

echo render_header();

echo '<h2>第一屆Post-中秋烤肉晚會</h2>';
echo '<p>為了響應中秋節期間不烤肉、節能減碳的活動，所以今年忍痛中斷了已經連續舉辦兩年的Pre-中秋烤肉晚會。</p>';
echo '<p>不過好消息是，只要避開中秋節期間，似乎就沒有問題了。所以今年特地挑中秋節過後兩週，趁月亮較小的時候，另闢新的活動：</p>';
echo '<p class="event">Post-中秋烤肉晚會</p>';
echo '<p>希望大家還是可以踴躍參加。</p>';

echo '<h3>日期/地點</h3>';
echo '<p class="event">2008/09/27 18:00</p>';
echo '<p class="event">老地方（地址翻去年的信吧～～～。）</p>';

echo '<h3>熱門食物</h3>';
echo render_popular_foods($user, 3);

$app_url = $fb->get_facebook_url('apps') . '/' . APP_SUFFIX;
echo '<fb:share-button class="meta">';
echo '<meta name="medium" content="news"/>';
echo '<meta name="title" content="來烤肉吧～～～" />';
echo '<meta name="description" content="加入 Adieu 來票選烤肉食材" />';
echo '<link rel="target_url" href="'.$app_url.'" />';
echo '</fb:share-button>';

echo render_footer();
