# How To Configure Instance Monitor

## Introduction To Monitor Configuration
	
The instance monitor configuration is located at eoncloud_web/local/local_settings.py. Here is a sample:

    MONITOR_CONFIG = {
        "enabled": True,
        "base_url": "http://14.14.14.101:5601",
        'monitors': [
            {
                "title": u"CPU",
                "url": "/#/visualize/edit/cpu?embed&_a=(filters:!(),linked:!f,query:(query_string:(analyze_wildcard:!t,query:'resource_id:!'{[{uuid}]}!'')),vis:(aggs:!((id:'1',params:(field:cpu_util),schema:metric,type:avg),(id:'2',params:(extended_bounds:(),field:'@timestamp',interval:{[{ interval }]},min_doc_count:1),schema:segment,type:date_histogram)),listeners:(),params:(addLegend:!f,addTooltip:!f,defaultYExtents:!f,shareYAxis:!t),type:line))"
            },
            {
                "title": u"磁盘",
                "url": "#/visualize/edit/disk?embed&_a=(filters:!(),linked:!f,query:(query_string:(analyze_wildcard:!t,query:'resource_id:{[{uuid}]}')),vis:(aggs:!((id:'1',params:(field:disk.read.bytes),schema:metric,type:avg),(id:'2',params:(field:disk.write.bytes),schema:metric,type:avg),(id:'3',params:(extended_bounds:(),field:'@timestamp',interval:{[{interval}]},min_doc_count:1),schema:segment,type:date_histogram)),listeners:(),params:(addLegend:!t,addTooltip:!t,defaultYExtents:!f,shareYAxis:!t),type:line))"
            },
            {
                "title": u"网络",
                "url": "#/visualize/edit/network?embed&_a=(filters:!(),linked:!f,query:(query_string:(analyze_wildcard:!t,query:'resource_id:{[{uuid}]}')),vis:(aggs:!((id:'1',params:(field:network.incoming.bytes.rate),schema:metric,type:avg),(id:'2',params:(field:network.outgoing.bytes.rate),schema:metric,type:avg),(id:'3',params:(extended_bounds:(),field:'@timestamp',interval:{[{interval}]},min_doc_count:1),schema:segment,type:date_histogram)),listeners:(),params:(addLegend:!t,addTooltip:!t,defaultYExtents:!f,shareYAxis:!t),type:line))"
            }
        ],
        'intervals': ['second', 'minute', 'hour', 'day', 'week', 'month']
    }

## Config Kibana URL

Monitor function is based on kibana, to protect kibana from attack, we put a proxy before kibana server to filter requests. Set your kibana url to MONITOR_CONFIG.base_url.

## Config Monitor Url

1. Get visualize share link. Take cpu line chart as example, the share link is :
 
		http://14.14.14.101:5601/#/visualize/edit/cpu?embed&_g=()&_a=(filters:!(),linked:!f,query:(query_string:(analyze_wildcard:!t,query:'resource_id:!'06e5fd14-8270-45d3-8bc9-d7767ab31233!'')),vis:(aggs:!((id:'1',params:(field:cpu_util),schema:metric,type:max),(id:'2',params:(extended_bounds:(),field:'@timestamp',interval:auto,min_doc_count:1),schema:segment,type:date_histogram)),listeners:(),params:(addLegend:!f,addTooltip:!f,defaultYExtents:!f,shareYAxis:!t),type:line))
		
2. Remove host. The host in cpu share link is: `http://14.14.14.101:5601/`, after
this part is removed, the share link now look like this:
	
		#/visualize/edit/cpu?embed&_g=()&_a=(filters:!(),linked:!f,query:(query_string:(analyze_wildcard:!t,query:'resource_id:!'06e5fd14-8270-45d3-8bc9-d7767ab31233!'')),vis:(aggs:!((id:'1',params:(field:cpu_util),schema:metric,type:max),(id:'2',params:(extended_bounds:(),field:'@timestamp',interval:auto,min_doc_count:1),schema:segment,type:date_histogram)),listeners:(),params:(addLegend:!f,addTooltip:!f,defaultYExtents:!f,shareYAxis:!t),type:line))
		
3. Remove _g Parameter. The origin share link has a parameter named ` _g ` during the query string which is unnecessary. After this parameter is remove, the url now looks like this:
	
		#/visualize/edit/cpu?embed&_a=(filters:!(),linked:!f,query:(query_string:(analyze_wildcard:!t,query:'resource_id:!'06e5fd14-8270-45d3-8bc9-d7767ab31233!'')),vis:(aggs:!((id:'1',params:(field:cpu_util),schema:metric,type:max),(id:'2',params:(extended_bounds:(),field:'@timestamp',interval:auto,min_doc_count:1),schema:segment,type:date_histogram)),listeners:(),params:(addLegend:!f,addTooltip:!f,defaultYExtents:!f,shareYAxis:!t),type:line))
		
4. Ensure `embed` parameter is in query string. Without `embed` paramter, the monitor view
will display a different page.

5. Make url template. 
	* resource_id (eg. `resource_id:!'06e5fd14-8270-45d3-8bc9-d7767ab31233!''))`). Change `06e5fd14-8270-45d3-8bc9-d7767ab31233` to `{[{ uuid }]}`.
	* interval (eg. `interval:auto,min_doc_count`). Change auto to `{[{ interval }]}`
6. The final link looks like this:

        #/visualize/edit/cpu?embed&_a=(filters:!(),linked:!f,query:(query_string:(analyze_wildcard:!t,query:'resource_id:!'{[{ uuid }]}!'')),vis:(aggs:!((id:'1',params:(field:cpu_util),schema:metric,type:max),(id:'2',params:(extended_bounds:(),field:'@timestamp',interval:{[{ interval }]},min_doc_count:1),schema:segment,type:date_histogram)),listeners:(),params:(addLegend:!f,addTooltip:!f,defaultYExtents:!f,shareYAxis:!t),type:line))
