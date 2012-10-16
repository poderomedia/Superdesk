define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('superdesk/request', 'models/request'),
    'tmpl!superdesk/request>list',
    'tmpl!superdesk/request>item',
    'tmpl!superdesk/request>use-request'
],
function($, superdesk, giz, Request)
{
    var 
    ItemView = giz.View.extend
    ({
        tagName: 'tr',
        model: null,
        events: 
        {
            '.view': { 'click': 'loadRequest' },
            '.request': { 'click': 'useRequest' }
        },
        useRequest: function(evt)
        {
            var pat = this.model.get('Pattern'),
                pattern = pat.replace(/\{(\d+)\}/g, '<label for="req-param-$1"><span class="badge badge-info">$1</span></label>'),
                p = pat.match(/\{(\d+)\}/g), 
                params = [],
                urlSlices = pat.split(/\{\d+\}/);
            for( var i in p )
                params.push
                ({ 
                    //html: p[i].replace(/\{(\d+)\}/g, '<span class="badge badge-info">$1</span>'), 
                    idx: p[i].replace(/\{|\}/g, '') 
                }); 
            $.tmpl('superdesk/request>use-request', {ServerUrl: superdesk.apiUrl+'/resources/', Params: params, Pattern: pattern}, function(e, o)
            {
                var o = $(o);
                o.modal()
                    .on('hide', function(){ o.remove(); })
                    .on('shown', function()
                    {
                        var self = $(this);
                        $(this).find('input:eq(0)').focus();
                        $(this).find('[data-action="use"]').on('click', function()
                        {
                            self.find('[data-is="param"]').each(function(i, e)
                            {  
                                urlSlices.splice(i+i+1, 0, $(e).val());
                            });
                            window.open( superdesk.apiUrl+'/resources/'+urlSlices.join(''), "_blank" );
                            o.modal('hide');
                        });
                    });
            });
            evt.preventDefault();
        },
        loadRequest: function(evt)
        {
            superdesk.showLoader();
            var theRequest = $(evt.target).attr('data-Request-link'), self = this;
            superdesk.getAction('modules.livedesk.edit')
            .done(function(action)
            {
                var callback = function()
                { 
                    require([superdesk.apiUrl+action.ScriptPath], function(EditApp){ EditApp(theRequest); }); 
                };
                action.ScriptPath && superdesk.navigation.bind( $(evt.target).attr('href'), callback, $(evt.target).attr('data-Request-title') );
            });
            evt.preventDefault();
        },
        init: function()
        {
            var self = this;
            this.model.on('read update', this.render, this);
            // this.model.on('delete', function(){ self.el.remove(); })
        },
        feedModel: function()
        {
            var d = this.model.feed();
            $(d).each(function()
            {
                this.origPattern = this.Pattern;
                this.Pattern = this.Pattern.replace(/\{(\d+)\}/g, '<span class="badge badge-info">$1</span>');
            });
            d.ServerUrl = superdesk.apiUrl+'/resources/'; 
            return d;
        },
        render: function()
        {
            $(this.el).tmpl('superdesk/request>item', {Request: this.feedModel ? this.feedModel() : this.model.feed()});
            $(this.el).prop('model', this.model).prop('view', this);
            $('.view', this.el).prop('model', this.model).prop('view', this);
            return this;
        },
        update: function(data)
        {
            for( var i in data ) this.model.set(i, data[i]);
            return this.model.sync();
        },
        /*remove: function()
        {
            this.model.remove().sync();
        },*/
        hide: function()
        {
            $(this.el).addClass('hide');
        },
        show: function()
        {
            $(this.el).removeClass('hide');
        }
    }),
    ListView = giz.View.extend
    ({
        users: null,
        events:
        {
            '[name="search"]': { 'keypress': 'key2Search' },
            '[data-action="search"]': { 'click': 'search' },
            '[data-action="cancel-search"]': { 'click': 'cancelSearch' },
            '.pagination a': { 'click': 'switchPage' }
        },
        
        key2Search: function(evt)
        {
            if(evt.keyCode == 27 ) 
            { 
                $('[data-action="cancel-search"]', this.el).trigger('click'); 
                evt.preventDefault(); 
            }
            if(evt.keyCode == 13) $('[data-action="search"]', this.el).trigger('click');
        },
        cancelSearch: function()
        {
            $('[name="search"]', this.el).val('');
            $('[data-action="search"]', this.el).trigger('click');
        },
        
        /*!
         * pagination handler
         */
        switchPage: function(evt)
        {
            if( this.syncing ) return;
            if( $(evt.target).attr('data-pagination') == 'currentpages' )
            {
                this.page.offset = $(evt.target).attr('data-offset');
                this.activate();
            }
            if( $(evt.target).attr('data-pagination') == 'prev' )
            {
                var o = parseInt(this.page.offset) - parseInt(this.page.limit);
                if( o >= 0 ) { this.page.offset = o; this.activate(); } 
            }
            if( $(evt.target).attr('data-pagination') == 'next' )
            {
                var o = parseInt(this.page.offset) + parseInt(this.page.limit);
                if( o < this.page.total ) { this.page.offset = o; this.activate(); } 
            }
        },
        /*!
         * search box handler
         */
        search: function()
        {
            var self = this,
                src = $('[name="search"]', self.el).val().toLowerCase();
            if( src.length <= 1 )
            {
                this.activate();
                $('[data-action="cancel-search"]', self.el).addClass('hide');
                return;
            }
            
            this.collection._list = []
            this.syncing = true;
            this.collection.xfilter('*').sync({data: {'title.ilike': '%'+src+'%'}, done: function(data){ self.syncing = false; }});
            
            $('[data-action="cancel-search"]', self.el).removeClass('hide');
        },
        /*!
         * a fix for gizmo.js view events bug
         */
        _resetEvents: false,
        init: function()
        {
            var self = this;
            
            this.page = { limit: 25, offset: 0, total: null, pagecount: 5 };
            
            this.collection = new (giz.Collection.extend({ model: Request, href: new giz.Url('Devel/Request') }));
            this.collection.on('read update', this.renderList, this);
            
            this._resetEvents = false;
        },
        activate: function()
        {
            if( this._resetEvents ) this.resetEvents();
            this._resetEvents = true;
            
            var self = this;
            this.collection._list = [];
            this.syncing = true;
            this.collection.xfilter('*').sync({data: {limit: this.page.limit, offset: this.page.offset},
                done: function(data){ self.syncing = false; self.page.total = data.total; self.render(); }});
        },
        
        addItem: function(model)
        {
            $('table tbody', this.el).append( (new ItemView({ model: model })).render().el );
        },
        
        paginate: function()
        {
            this.page.currentpages = [];
            for( var i= -this.page.pagecount/2; i < this.page.pagecount/2; i++ )
            {
                var x = parseInt(this.page.offset) + (Math.round(i) * this.page.limit);
                if( x < 0 || x >= this.page.total ) continue;
                var currentpage = {offset: x, page: (x/this.page.limit)+1};
                if( Math.round(i) == 0 ) currentpage.className = 'active';
                this.page.currentpages.push(currentpage);
            }
        },
        
        renderList: function()
        {
            $('table tbody', this.el).html('');
            var self = this;
            this.collection.each(function(){ self.addItem(this); });
        },
        
        render: function()
        {
            this.paginate();
            var data = {pagination: this.page},
                self = this;
            superdesk.applyLayout('superdesk/request>list', data, function()
            {
                // new ItemView for each models 
                self.renderList();
            });
            $.superdesk.hideLoader();
        }
        
    }),
    // TODO table partial view
    ListView1 = ListView.extend({}),
    listView = new ListView1({ el: '#area-main' }); 
    
    return function(){ listView.activate(); };
});

