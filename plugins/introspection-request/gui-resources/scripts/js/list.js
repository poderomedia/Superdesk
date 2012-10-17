define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('superdesk/request', 'models/request'),
    'tmpl!superdesk/request>main',
    'tmpl!superdesk/request>list',
    'tmpl!superdesk/request>request-item',
    'tmpl!superdesk/request>input-item',
    'tmpl!superdesk/request>use-request'
],
function($, superdesk, giz, Request)
{
    var 
    RequestItemView = giz.View.extend
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
                        $('form', self).on('submit', function(evt){ $('[data-action="use"]', self).trigger('click'); evt.preventDefault(); });
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
            $(this.el).tmpl('superdesk/request>request-item', {Request: this.feedModel ? this.feedModel() : this.model.feed()});
            $(this.el).prop('model', this.model).prop('view', this);
            $('.view', this.el).prop('model', this.model).prop('view', this);
            return this;
        },
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
            this.filterCollection();
            
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
            
            this.collection = self.getCollection();
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
            var self = this;
            this.clearItems();
            this.collection.each(function(){ self.addItem(this); });
        },
        
        render: function()
        {
            this.paginate();
            var data = {pagination: this.page},
                self = this;
            $.tmpl(self.mainTemplate, data, function(e, o)
            {
                self.el.html('').append(o);
                self.renderList();
            });
            $.superdesk.hideLoader();
        },
        /*!
         * for implementation
         */
        mainTemplate: '',
        addItem: $.noop,
        clearItems: $.noop,
        getCollection: $.noop,
        filterCollection: $.noop
    }),

    RequestListView = ListView.extend
    ({
        mainTemplate: 'superdesk/request>list',
        getCollection: function()
        {
            return new (giz.Collection.extend({ model: Request, href: new giz.Url('Devel/Request') }));
        },
        filterCollection: function()
        {
            var self = this;
            return this.collection.xfilter('*').sync({data: {'title.ilike': '%'+src+'%'}, done: function(data){ self.syncing = false; }});
        },
        addItem: function(model)
        {
            $('table tbody', this.el).append( (new RequestItemView({ model: model })).render().el );
        },
        clearItems: function()
        {
            $('table tbody', this.el).html('');
        }
    }),
    
    InputListView = ListView.extend
    ({
        
    }),
    
    MainView = giz.View.extend
    ({
        events:
        { 
            '.nav-tabs a':{ 'click': 'tabs' } 
        },
        tabs: function(evt)
        {
            evt.preventDefault(); 
            $(evt.currentTarget).tab('show');  
        },
        requestListView: null,
        inputListView: null,
        activate: function()
        {
            var self = this;
            this.render(function()
            { 
                $(superdesk.layoutPlaceholder).html(self.el);
            });
        },
        getInputListView: function()
        {
            if( !this.inputListView )
                this.inputListView = new InputListView();
            return this.inputListView;
        },
        getRequestListView: function()
        {
            if( !this.requestListView )
                this.requestListView = new RequestListView();
            return this.requestListView
        },
        render: function(cb)
        {
            var self = this;
            $.tmpl('superdesk/request>main', {}, function(e, o)
            {
                self.el.append(o);
                self.getRequestListView().setElement(self.el.find('#requests')).activate();
                $.isFunction(cb) && cb.apply(self);
            });
        }
    });
    
    mainView = new MainView({ tagName: 'span' });
    
    return function(){ mainView.activate(); };
});

