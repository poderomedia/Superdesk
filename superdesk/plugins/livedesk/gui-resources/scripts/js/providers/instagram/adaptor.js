define('providers/instagram/adaptor', 
[
    'providers',
    'utils/str',
    'jquery',
    'gizmo',
    'jquery/rest',
    'jquery/utils',
    'providers/instagram/tab',
    'tmpl!livedesk>providers/instagram/post'
], 
function(providers,str, $, Gizmo)
{
    var AnnotateView = Gizmo.View.extend
    ({
        tagName: 'li',
        init: function(data)
        {
            var self = this;
            $(self.el).on('click', '.btn.publish', function()
            {
                self.data.Content = $('.instagram-full-content .result-text', self.el).html();
                self.data.Meta.annotation = [$('.instagram-full-content .annotation:eq(0)', self.el).html(), $('.instagram-full-content .annotation:eq(1)', self.el).html()];
                self.data.Meta = JSON.stringify(self.data.Meta);
                self.parent.insert(self.data, self);
                $('.actions', self.el).remove();
            })
			.on('click', '.btn.cancel', function()
            {
                self.parent = null;
                self.el.remove();
            })
			.on('click', 'a.close', function(){
				$('#delete-post .yes')
					.off(self.getEvent('click'))
					.on(self.getEvent('click'), function(){
						self.parent = null;
						self.el.remove();
					});				
			});
			
        },
        render: function()
        {
            this.el.tmpl('livedesk>providers/instagram/post', this.data);
            this.el.addClass('with-avatar instagram clearfix');
            $('.actions', this.el).removeClass('hide');
        }
    });
    
    $.extend(providers.instagram, 
    {
        adaptor: 
        {
            author: 1,
            init: function() 
            {
                var self = this;
                new $.rest('Superdesk/Collaborator/')
                    .xfilter('Id')
                    .request({data: { 'qs.name': 'instagram'}})
                    .done(function(collabs)
                    {
                        if($.isDefined(collabs[0])) 
                            self.author = collabs[0].Id;
                    });
            },
            universal: function(obj) 
            {
                var meta =  jQuery.extend(true, {}, obj);                
                return new AnnotateView
                ({
                    data: 
                    {
                        Content: obj.images.standard_resolution.url,
                        Type: 'normal',
                        Author: this.author,
                        Meta: meta
                    }
                });
            },
        }
    });
	return providers;
});

