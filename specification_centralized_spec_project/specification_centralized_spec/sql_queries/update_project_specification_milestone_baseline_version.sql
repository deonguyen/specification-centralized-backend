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
    %s AS project_id,
    %s AS project_milestone_id,
    %s AS user_id,
    ps.id AS project_specification_id,
    sr.specification_id,
    sr.id AS specification_revision_id
FROM public.project_specification ps
JOIN public.specification_revision sr 
  ON sr.specification_id = ps.specification_id AND sr.project_id = ps.project_id
WHERE ps.id = %s 
  AND sr.version = %s
ON CONFLICT (
    project_id, 
    project_milestone_id, 
    user_id, 
    project_specification_id
) 
DO UPDATE SET 
    specification_id = EXCLUDED.specification_id,
    specification_revision_id = EXCLUDED.specification_revision_id;