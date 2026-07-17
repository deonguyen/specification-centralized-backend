SELECT 
    ps.id AS project_specification_id,
    ps.project_id,
    p.name AS project_name,
    s.name AS specification_name,
    ps.category1,
    ps.category2,
    ts.id AS test_suite_id,
    ts.name AS test_suite_name,
    ts.code AS test_suite_code,
    ts.status AS test_suite_status,
    tc.id AS test_case_id,
    tc.name AS test_case_name,
    tc.code AS test_case_code,
    tc.status AS test_case_status,
    tc.description AS test_case_description,
    tc.steps AS test_case_steps,
    tc.expected_result,
    tc.actual_result
FROM project_specification ps
LEFT JOIN project p ON ps.project_id = p.id
LEFT JOIN specification s ON ps.specification_id = s.id
LEFT JOIN specification_test_suite ts ON ps.project_id = ts.project_id AND ps.specification_id = ts.specification_id
LEFT JOIN specification_test_case tc ON ts.id = tc.specification_test_suite_id
WHERE 1=1