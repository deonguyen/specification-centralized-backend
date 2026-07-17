
SELECT 
    ps.id AS project_specification_id,
    ps.project_id,
    p.name AS project_name,
    c.name AS component_name,
    f.name AS function_name,
    s.name AS specification_name,
    s.id AS specification_id,
    s.type AS specification_type,
    s.version AS specification_version,
    s.content AS specification_content,
    s.raw_content AS specification_raw_content,
    s.interface AS specification_interface,
    parent_s.name AS parent_name,
    ps.category1,
    ps.category2,
    ps.specification_revision_id AS latest_specification_revision_id,
    latest_sr.version AS latest_specification_revision_version,
    latest_sr.content AS latest_specification_revision_content,
    latest_sr.raw_content AS latest_specification_revision_raw_content,
    latest_sr.interface AS latest_specification_revision_interface,
    -- Dynamically pivot every milestone ID into a JSON object acting as your columns
    jsonb_object_agg(
        pm.name::text, 
        jsonb_build_object(
            'version', sr.version, 
            'project_milestone_id', psmb.project_milestone_id, 
            'project_specification_id', psmb.project_specification_id,
            'specification_revision_id', psmb.specification_revision_id,
            'specification_revision_raw_content', sr.raw_content,
            'specification_revision_content', sr.content,
            'specification_revision_interface', sr.interface
        )
    ) FILTER (WHERE pm.id IS NOT NULL) AS milestones
FROM 
    project_specification ps
LEFT JOIN 
    project p ON ps.project_id = p.id
LEFT JOIN 
    component c ON ps.component_id = c.id
LEFT JOIN 
    function f ON ps.function_id = f.id
LEFT JOIN 
    specification s ON ps.specification_id = s.id
LEFT JOIN 
    project_specification parent_ps ON ps.parent_id = parent_ps.id
LEFT JOIN 
    specification parent_s ON parent_ps.specification_id = parent_s.id
LEFT JOIN 
    specification_revision latest_sr ON ps.specification_revision_id = latest_sr.id
LEFT JOIN 
    project_specification_milestone_baseline psmb 
    ON ps.id = psmb.project_specification_id
LEFT JOIN 
    specification_revision sr
    ON psmb.specification_revision_id = sr.id
LEFT JOIN 
    project_milestone pm 
    ON psmb.project_milestone_id = pm.id
GROUP BY 
    ps.id, ps.project_id, p.name, c.name, f.name, s.name, s.id, s.type, s.version, s.content, s.raw_content, s.interface, parent_s.name, ps.category1, ps.category2, ps.specification_revision_id, latest_sr.version, latest_sr.content, latest_sr.raw_content, latest_sr.interface
ORDER BY 
    component_name, function_name, parent_name, specification_name, ps.id;