<?php
header('Content-Type: application/json');

// Get JSON input
$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!$data) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid JSON']);
    exit;
}

$logFile = 'exam_logs.txt';

$timestamp = date('Y-m-d H:i:s');
$studentName = isset($data['payload']['student_name']) ? $data['payload']['student_name'] : 'Unknown';
$studentEmail = isset($data['payload']['student_email']) ? $data['payload']['student_email'] : 'Unknown';
$totalScore = isset($data['payload']['total_score']) ? $data['payload']['total_score'] : 'N/A';
$dbStatus = isset($data['db_status']) ? $data['db_status'] : 'Unknown';
$dbMessage = isset($data['db_message']) ? $data['db_message'] : '';

$logEntry = "======================================================================\n";
$logEntry .= "Date/Time: " . $timestamp . "\n";
$logEntry .= "Student: " . $studentName . " (" . $studentEmail . ")\n";
$logEntry .= "Total Score: " . $totalScore . "\n";
$logEntry .= "----------------------------------------------------------------------\n";
$readableLog = isset($data['readable_log']) ? $data['readable_log'] : json_encode($data['payload'], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);

$logEntry .= "ANSWERS:\n";
$logEntry .= $readableLog . "\n";
$logEntry .= "----------------------------------------------------------------------\n";
$logEntry .= "SUPABASE INSERT STATUS: " . strtoupper($dbStatus) . "\n";
if ($dbMessage) {
    $logEntry .= "SUPABASE MESSAGE/ERROR: " . json_encode($dbMessage) . "\n";
}
$logEntry .= "======================================================================\n\n";

if (file_put_contents($logFile, $logEntry, FILE_APPEND | LOCK_EX) !== false) {
    // Also save raw JSON to a backup file for system recovery
    if (isset($data['payload'])) {
        file_put_contents('exam_backup.jsonl', json_encode($data['payload']) . "\n", FILE_APPEND | LOCK_EX);
    }
    echo json_encode(['success' => true]);
} else {
    http_response_code(500);
    echo json_encode(['error' => 'Failed to write log file']);
}
?>
