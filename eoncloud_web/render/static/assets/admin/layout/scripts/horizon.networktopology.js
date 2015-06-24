/* Namespace for core functionality related to Network Topology. */

horizon.network_topology = {
  model: null,
  fa_globe_glyph: '\uf0ac',
  fa_globe_glyph_width: 15,
  svg:'#topology_canvas',
  svg_container:'#topologyCanvasContainer',
  post_messages:'#topologyMessages',
  network_tmpl:{
    small:'#topology_tml > .network_container_small',
    normal:'#topology_tml > .network_container_normal'
  },
  router_tmpl: {
    small:'#topology_tml > .router_container_normal',
    normal:'#topology_tml > .router_container_normal'
  },
  instance_tmpl: {
    small:'#topology_tml > .instance_small',
    normal:'#topology_tml > .instance_normal'
  },
  balloon_tmpl : null,
  balloon_device_tmpl : null,
  balloon_port_tmpl : null,
  network_index: {},
  balloon_id:null,
  reload_duration: 10000,
  draw_mode:'normal',
  network_height : 0,
  previous_message : null,
  element_properties:{
    normal:{
      network_width:270,
      network_min_height:800,
      top_margin:80,
      default_height:50,
      margin:20,
      device_x:98.5,
      device_width:90,
      port_margin:16,
      port_height:6,
      port_width:82,
      port_text_margin:{x:6,y:-4},
      texts_bg_y:32,
      type_y:46,
      balloon_margin:{x:12,y:-12}
    },
    small :{
      network_width:100,
      network_min_height:400,
      top_margin:50,
      default_height:20,
      margin:30,
      device_x:47.5,
      device_width:20,
      port_margin:5,
      port_height:3,
      port_width:32.5,
      port_text_margin:{x:0,y:0},
      texts_bg_y:0,
      type_y:0,
      balloon_margin:{x:12,y:-30}
    },
    cidr_margin:5,
    device_name_max_size:9,
    device_name_suffix:'..'
  },
  init:function() {
    var self = this;
    //$(self.svg_container).spin(horizon.conf.spinner_options.modal);
    /*if($('#networktopology').length === 0) {
      return;
    }*/
    self.color = d3.scale.category10();
    /*self.balloon_tmpl = Hogan.compile($('#balloon_container').html());
    self.balloon_device_tmpl = Hogan.compile($('#balloon_device').html());
    self.balloon_port_tmpl = Hogan.compile($('#balloon_port').html());*/

    $('.toggleView > .btn').click(function(){
      self.draw_mode = $(this).data('value');
      $('g.network').remove();
      horizon.cookies.put('ntp_draw_mode',self.draw_mode);
      self.data_convert();
    });

    $(window)
      .on('message',function(e){
        var message = $.parseJSON(e.originalEvent.data);
        if (self.previous_message !== message.message) {
          horizon.alert(message.type, message.message);
          horizon.autoDismissAlerts();
          self.previous_message = message.message;
          self.delete_post_message(message.iframe_id);
          self.load_network_info();
          setTimeout(function() {
            self.previous_message = null;
          },10000);
        }
      });

    self.load_network_info();
  },
  load_network_info:function(){
    var self = this;
    /*if($('#networktopology').length === 0) {
      return;
    }*/

    self.data_convert();
  },
  select_draw_mode:function() {
    /*var self = this;
    var draw_mode = horizon.cookies.get('ntp_draw_mode');
    if (draw_mode && (draw_mode === 'normal' || draw_mode === 'small')) {
      self.draw_mode = draw_mode;
    } else {
      if (self.model.networks.length *
        self.element_properties.normal.network_width >  $('#topologyCanvas').width()) {
        self.draw_mode = 'small';
      } else {
        self.draw_mode = 'normal';
      }
      horizon.cookies.put('ntp_draw_mode',self.draw_mode);
    }
    $('.toggleView > .btn').each(function(){
      var $this = $(this);
      if($this.data('value') === self.draw_mode) {
        $this.addClass('active');
      } else {
        $this.removeClass('active');
      }
    });*/
  },
  data_convert:function() {
    var self = this;
    var model = self.model;

    $.each(model.networks, function(index, network) {
      network.devices = [];
      $.each(model.instances,function(index, instance) {
          if(network.id === instance.network_id) {
            network.devices.push(instance);
          }
      });
    });
    $.each(model.routers, function(index, router) {
      router.networks = [];
      $.each(model.networks,function(index, network) {
        $.each(model.router_interfaces,function(index,router_interface){
          if (router.id == router_interface.router && router_interface.network_id == network.id){
            router.networks.push(network)
            return false;
          }
        });
      });
    });
    var orther_networks = []
    $.each(model.networks,function(index, network) {
      var flag = false;
      $.each(model.router_interfaces,function(index,router_interface){
        if (router_interface.network_id == network.id){
            flag = true;
          return false;
        }
      });
      if(!flag){
        orther_networks.push(network);
      }
    });
    model.routers.push({"id":0,"networks":orther_networks});

    self.draw_topology();
  },
  draw_topology:function() {
    var self = this;

    var svg = d3.select(self.svg);
    var element_properties = self.element_properties[self.draw_mode];
    svg
      .attr('width',self.model.networks.length*element_properties.network_width)
      .attr('height',760);

    var network_num = 0;
    //Â·ÓÉÆ÷
    var router = svg.selectAll('g.router')
        .data(self.model.routers);
    var router_enter  = router.enter()
        .append('g')
        .attr('class','router')
        .each(function(d,i){
          if(d.name !=undefined){
            this.appendChild(d3.select(self.router_tmpl[self.draw_mode]).node().cloneNode(true));
            this.appendChild(d3.select('.router_line_normal').node().cloneNode(true));
          }
        });
    router
        .attr('id',function(d){return 'router_'+ d.id;})
        .attr('transform',function(d,i){
        console.log(network_num)
          var width =0;
          width =network_num * element_properties.network_width +(i)*10
          network_num  = network_num+(d.networks.length >0 ?d.networks.length:1)
          return 'translate(' + width + ',' + 90 + ')';
        });
    router.select('.router_container_normal').attr('transform',function(d){
        var network_length = d.networks.length >0 ?d.networks.length:1
        var width = network_length * element_properties.network_width/2 - 60
      return 'translate(' + width + ',' + 0 + ')';
    });
    router.select('.router_line_normal .router-line-h').attr('x1',function(d){
      var network_length = d.networks.length >0 ?d.networks.length:1
      var width = network_length * element_properties.network_width/2
      return width;
    }).attr('x2',function(d){
      var network_length = d.networks.length >0 ?d.networks.length:1
      var width = network_length * element_properties.network_width/2
      return width;
    });
    router.select('.router_line_normal .router-line-v').attr('x2',function(d){
      var network_length = d.networks.length >0 ?d.networks.length:1
      var width = network_length * element_properties.network_width
      return width;
    });
    router.select('.router_container_normal .router-line').attr('y2',function(d){
      if(d.is_gateway){
        return -90;
      }
    });
    router.select('.router-gateway').text(function(d){
      return d.gateway;
    });
    router.select('.router-text').text(function(d){
      return d.name;
    });


    svg.attr('width',network_num * element_properties.network_width);
    $('#topoTop').css('width',network_num * element_properties.network_width);
    //½âÎöÍøÂç
    var network = router.selectAll('g.network').data(function(d){
     return d.networks
    });
    var network_enter = network.enter().append('g').attr('class','network').each(function(d,i){
      this.appendChild(d3.select(self.network_tmpl[self.draw_mode]).node().cloneNode(true));
    });
    network
        .attr('id',function(d){return 'netowrk_'+ d.id;})
        .attr('transform',function(d,i){
          return 'translate(' + element_properties.network_width * i + ',' + 170 + ')';
        });
    network.select(".network-name").text(function(d){
      return d.name;
    })
    network.select(".network-cidr").text(function(d){
      console.log(d)
      return d.address;
    })

    var device = network.selectAll('g.device').data(function(d){return d.devices});
    var device_enter = device.enter().append('g').attr('class','device').each(function(d,i){
      this.appendChild(d3.select(self.instance_tmpl[self.draw_mode]).node().cloneNode(true));
    });
    device.attr('id',function(d){return 'device_'+ d.id});
    device.attr('transform',function(d,i){
      return 'translate(' + element_properties.device_x + ',' + 100  + ')';
    });

    device.select(".texts .name").text(function(d){
      return d.name;
    });
    device.select(".ports .port .port_text").text(function(d){
      return d.private_ip;
    });

  },
  get_network_color: function(network_id) {
    return this.color(this.get_network_index(network_id));
  },
  get_network_index: function(network_id) {
    return this.network_index[network_id];
  },
  select_port: function(device_id){
    return $.map(this.model.ports,function(port, index){
      if (port.device_id === device_id) {
        return port;
      }
    });
  },
  select_main_port: function(ports){
    var _self = this;
    var main_port_index = 0;
    var MAX_INT = 4294967295;
    var min_port_length = MAX_INT;
    $.each(ports, function(index, port){
      var port_length = _self.sum_port_length(port.network_id, ports);
      if(port_length < min_port_length){
        min_port_length = port_length;
        main_port_index = index;
      }
    });
    return ports[main_port_index];
  },
  sum_port_length: function(network_id, ports){
    var self = this;
    var sum_port_length = 0;
    var base_index = self.get_network_index(network_id);
    $.each(ports, function(index, port){
      sum_port_length += base_index - self.get_network_index(port.network_id);
    });
    return sum_port_length;
  },
  string_truncate: function(string) {
    var self = this;
    var str = string;
    var max_size = self.element_properties.device_name_max_size;
    var suffix = self.element_properties.device_name_suffix;
    var bytes = 0;
    for (var i = 0;  i < str.length; i++) {
      bytes += str.charCodeAt(i) <= 255 ? 1 : 2;
      if (bytes > max_size) {
        str = str.substr(0, i) + suffix;
        break;
      }
    }
    return str;
  },
  delete_device: function(type, device_id) {
    var self = this;
    var message = {id:device_id};
    self.post_message(device_id,type,message);
  },
  delete_port: function(router_id, port_id) {
    var self = this;
    var message = {id:port_id};
    self.post_message(port_id, 'router/' + router_id + '/', message);
  },
  show_balloon:function(d,element) {
    var self = this;
    var element_properties = self.element_properties[self.draw_mode];
    if (self.balloon_id) {
      self.delete_balloon();
    }
    var balloon_tmpl = self.balloon_tmpl;
    var device_tmpl = self.balloon_device_tmpl;
    var port_tmpl = self.balloon_port_tmpl;
    var balloon_id = 'bl_' + d.id;
    var ports = [];
    $.each(d.ports,function(i, port){
      var object = {};
      object.id = port.id;
      object.router_id = port.device_id;
      object.url = port.url;
      object.port_status = port.status;
      object.port_status_css = (port.status === "ACTIVE")? 'active' : 'down';
      var ip_address = '';
      try {
        ip_address = port.fixed_ips[0].ip_address;
      }catch(e){
        ip_address = gettext('None');
      }
      var device_owner = '';
      try {
        device_owner = port.device_owner.replace('network:','');
      }catch(e){
        device_owner = gettext('None');
      }
      object.ip_address = ip_address;
      object.device_owner = device_owner;
      object.is_interface = (device_owner === 'router_interface');
      ports.push(object);
    });
    var html_data = {
      balloon_id:balloon_id,
      id:d.id,
      url:d.url,
      name:d.name,
      type:d.type,
      delete_label: gettext("Delete"),
      status:d.status,
      status_class:(d.status === "ACTIVE")? 'active' : 'down',
      status_label: gettext("STATUS"),
      id_label: gettext("ID"),
      interfaces_label: gettext("Interfaces"),
      delete_interface_label: gettext("Delete Interface"),
      open_console_label: gettext("Open Console"),
      view_details_label: gettext("View Details")
    };
    if (d.type === 'router') {
      html_data.delete_label = gettext("Delete Router");
      html_data.view_details_label = gettext("View Router Details");
      html_data.port = ports;
      html_data.add_interface_url = d.url + 'addinterface';
      html_data.add_interface_label = gettext("Add Interface");
      html = balloon_tmpl.render(html_data,{
        table1:device_tmpl,
        table2:(ports.length > 0) ? port_tmpl : null
      });
    } else if (d.type === 'instance') {
      html_data.delete_label = gettext("Terminate Instance");
      html_data.view_details_label = gettext("View Instance Details");
      html_data.console_id = d.id;
      html_data.console = d.console;
      html = balloon_tmpl.render(html_data,{
        table1:device_tmpl
      });
    } else {
      return;
    }
    $(self.svg_container).append(html);
    var device_position = element.find('.frame');
    var x = device_position.position().left +
      element_properties.device_width +
      element_properties.balloon_margin.x;
    var y = device_position.position().top +
      element_properties.balloon_margin.y;
    $('#' + balloon_id).css({
      'left': x + 'px',
      'top': y + 'px'
    })
      .show();
    var $balloon = $('#' + balloon_id);
    if ($balloon.offset().left + $balloon.outerWidth() > $(window).outerWidth()) {
      $balloon
        .css({
          'left': 0 + 'px'
        })
        .css({
          'left': (device_position.position().left - $balloon.outerWidth() -
            element_properties.balloon_margin.x + 'px')
        })
        .addClass('leftPosition');
    }
    $balloon.find('.delete-device').click(function(e){
      var $this = $(this);
      $this.prop('disabled', true);
      d3.select('#id_' + $this.data('device-id')).classed('loading',true);
      self.delete_device($this.data('type'),$this.data('device-id'));
    });
    $balloon.find('.delete-port').click(function(e){
      var $this = $(this);
      self.delete_port($this.data('router-id'),$this.data('port-id'));
    });
    self.balloon_id = balloon_id;
  },
  delete_balloon:function() {
    var self = this;
    if(self.balloon_id) {
      $('#' + self.balloon_id).remove();
      self.balloon_id = null;
    }
  },
  post_message: function(id,url,message) {
    var self = this;
    var iframe_id = 'ifr_' + id;
    var iframe = $('<iframe width="500" height="300" />')
      .attr('id',iframe_id)
      .attr('src',url)
      .appendTo(self.post_messages);
    iframe.on('load',function() {
      $(this).get(0).contentWindow.postMessage(
        JSON.stringify(message, null, 2), '*');
    });
  },
  delete_post_message: function(id) {
    $('#' + id).remove();
  }
};
