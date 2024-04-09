-- DROP VIEW IF EXISTS momain_dash;

CREATE OR REPLACE VIEW momain_dash AS
WITH data AS (
select
cs.campaign_id,
cs.school_id,
ARRAY[
coalesce(count(distinct t.extid) filter (where t.direction=0), 0)::bigint,
coalesce(count(distinct t.extid) filter (where t.direction=1), 0)::bigint
] as received
from momain_campaign_schools cs
left join momain_trip t using(campaign_id,school_id)
group by 1,2
)
select
c.id as campaign_id,
s.id as school_id,
ARRAY[
s.students,
s.students
] as expected,
data.received,
s.uuid,
s.name,
s.code,
s.students,
s.address,
s.lat,
s.lng
from data
join momain_campaign c on c.id=data.campaign_id
join momain_school s on s.id=data.school_id
order by c.stamp_start DESC, c.stamp_end DESC, s.name;

ALTER VIEW momain_dash OWNER TO django;


-- DROP VIEW momain_dashheat;

CREATE OR REPLACE VIEW momain_dashheat AS
WITH stage AS (
select
*
from momain_stage
order by ord
),
data AS (
select
t.extid,
t.campaign_id,
t.school_id,
s.mode,
sum(tt.trav_dist) as trav_dist,
sum(tt.trav_time) as trav_time
from momain_trip t
join stage s on s.trip_id=t.id
join momain_trait tt on tt.stage_id=s.id
where t.direction >= 0
group by 1,2,3,4
order by 1,2,3
),
data2 AS (
select
extid,
campaign_id,
school_id,
array_agg(mode) as modes,
1.0::float as flow,
sum(trav_dist) as trav_dist,
sum(trav_time) as trav_time
from data
group by 1,2,3
)
select
data2.*,
t.direction as dir,
CASE WHEN t.direction = 0 THEN t.orig_geom ELSE t.dest_geom END as geom
from data2
join momain_trip t using(extid)
where t.direction >= 0
order by 1,2,3;

ALTER VIEW momain_dashheat OWNER TO django;


-- DROP VIEW momain_dashtrip;

CREATE OR REPLACE VIEW momain_dashtrip AS
select
t.campaign_id,
t.school_id,
s.mode,
l.network_id,
l.netid,
count(*) as flow
from momain_trip t
join momain_stage s on s.trip_id=t.id
join momain_trait tt on tt.stage_id=s.id
join momain_link l on l.id=tt.link_id
group by 1,2,3,4,5
order by 1,2,3,4,5;

ALTER VIEW momain_dashtrip OWNER TO django;


-- DROP VIEW momain_dashlink;

CREATE OR REPLACE VIEW momain_dashlink AS
SELECT 
q.campaign_id,
jsonb_build_object(
	'type', 'FeatureCollection',
	'features', json_agg(ST_AsGeoJSON(q.*)::json)
) as data
FROM ( 
	WITH data AS (
		select
		t.campaign_id,
		t.school_id,
		t.direction as dir,
		s.mode,
		l.network_id,
		l.netid,
		count(*) as flow
		from momain_trip t
		join momain_stage s on s.trip_id=t.id
		join momain_trait tt on tt.stage_id=s.id
		join momain_link l on l.id=tt.link_id
		group by 1,2,3,4,5,6
	),
	data2 AS (
		select
		campaign_id,
		network_id,
		netid,
		json_agg(
			jsonb_build_object(
				'school_id',   school_id,
				'dir', 		dir,
				'mode',   	mode,
				'flow',		flow
			)
		) as data
		from data
		group by 1,2,3
	)
	select
	data2.*,
	round(st_length(l.geom::geography)::numeric,3) as trav_dist,
	l.geom
	from data2
	join momain_link l using(network_id,netid)
	order by 1,2,3
) q
group by 1;

ALTER VIEW momain_dashlink OWNER TO django;
