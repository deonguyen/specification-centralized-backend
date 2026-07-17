SELECT 
    ps.id,
    ps.project_id,
    c.name AS component_name,
    f.name AS function_name,
    parent_s.name AS parent_name,
    p.name AS project_name,
    s.name AS specification_name,
    ps.category1,
    sr.version,
    sr.change_summary
FROM 
    project_specification ps
LEFT JOIN project p ON ps.project_id = p.id
LEFT JOIN specification s ON ps.specification_id = s.id
LEFT JOIN component c ON ps.component_id = c.id
LEFT JOIN function f ON ps.function_id = f.id
LEFT JOIN project_specification parent_ps ON ps.parent_id = parent_ps.id
LEFT JOIN specification parent_s ON parent_ps.specification_id = parent_s.id
LEFT JOIN (
    SELECT 
        specification_id, 
        version, 
        change_summary,
        ROW_NUMBER() OVER(PARTITION BY specification_id ORDER BY change_date DESC) as rn
    FROM specification_revision
) sr ON sr.specification_id = s.id AND sr.rn = 1;