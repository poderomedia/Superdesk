define
([
    'gizmo/superdesk', 'jquery', 
    config.guiJs('superdesk/article', 'models/article-ctx'),
    config.guiJs('superdesk/article', 'models/article'),
    'tmpl!superdesk/article>list',
    'tmpl!superdesk/article>item'
],
function(giz, $, ArticleCtx, Article)
{
    var dummyTypes = {1: 'Text', 2: 'Web', 3: 'Smartphone', 4: 'Tablet'},
    ItemView = giz.View.extend
    ({
        init: function()
        {
            //this.setElement($('<div />'));
        },
        render: function(ctx)
        {
            var cssClass = 'ctx-'+ctx.get('Type'),
                content = ctx.get('Content'),
                self = this;
            $.tmpl('superdesk/article>item', {ViewClass: cssClass, Content:content}, function()
            { 
                self.setElement($(arguments[1]));
            });
            return this;
        }
    }),
    ListView = giz.View.extend
    ({
        article: null,
        contexts: null,
        init: function()
        {
            // this.contexts = new (giz.Collection.extend({ model: ArticleCtx }));
            // and bind to events here, then on activate sync with thier url from article
        },
        activate: function(href)
        {
            var self = this;
            this.article = new Article(href);
            this.contexts = this.article.get('ArticleCtx');
            this.contexts
                .xfilter('*')
                .sync(this.article.get('ArticleCtx').href)
                .done(function(){ self.render(); });
        },
        addItem : function(ctx)
        {
            $('#article-views-main', self.el).append((new ItemView).render(ctx).el);
        },
        render: function()
        {
            var data = {},
                self = this;
            $.superdesk.applyLayout('superdesk/article>list', data, function()
            {
                // new ItemView for each models 
                self.contexts.each(function(){ self.addItem(this); });
            });
            $.superdesk.hideLoader();
        }
    });
    
    listView = new ListView({ el: '#area-main' }); 
    
    return function(article)
    {
        listView.activate(article);
    };
});