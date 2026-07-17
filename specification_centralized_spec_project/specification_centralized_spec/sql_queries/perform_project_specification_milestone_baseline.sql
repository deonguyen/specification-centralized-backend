INSERT INTO public.project_specification_milestone_baseline
(
    project_id, 
    project_milestone_id, 
    user_id, 
    project_specification_id, 
    specification_id, 
    specification_revision_id
)
SELECT 
    ps.project_id,
    %s as project_milestone_id,
    %s as user_id,
    ps.id as project_specification_id,
    sr.specification_id,
    sr.id as specification_revision_id
FROM public.project_specification ps
JOIN public.specification_revision sr ON ps.specification_revision_id = sr.id
WHERE ps.project_id = %s AND sr.version = %s
ON CONFLICT (
    project_id, 
    project_milestone_id, 
    user_id, 
    project_specification_id
) 
DO UPDATE SET 
    project_id = EXCLUDED.project_id,
    user_id = EXCLUDED.user_id,
    specification_id = EXCLUDED.specification_id,
    specification_revision_id = EXCLUDED.specification_revision_id;
