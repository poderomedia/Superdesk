define('providers/flickr/adaptor', 
[
    'providers',
    'utils/str',
    'jquery',
    'gizmo',
    'jquery/rest',
    'jquery/utils',
    'providers/flickr/tab',
    'tmpl!livedesk>providers/flickr/post'
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
                self.data.Content = $('.flickr-full-content .result-text', self.el).html();
                self.data.Meta.annotation = $('.flickr-full-content .annotation:eq(0)', self.el).html();
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
            this.el.tmpl('livedesk>providers/flickr/post', this.data);
            this.el.addClass('with-avatar twitter clearfix');
            $('.actions', this.el).removeClass('hide');
        }
    });
    
    $.extend(providers.flickr, 
    {
        adaptor: 
        {
            author: 1,
            init: function() 
            {
                var self = this;
                new $.rest('Superdesk/Collaborator/')
                    .xfilter('Id')
                    .request({data: { 'qs.name': 'flickr'}})
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
                        Content: obj.title,
                        Type: 'normal',
                        Author: this.author,
                        Meta: meta
                    }
                });
            },
            universalOld: function(content) {
                var myClone = content.clone();
                myClone.find('time').remove();
                
                var data = {
                    Content: myClone.find('.result-content').html(),
                    Type: 'normal',
                    Author: this.author
                };
                return data;
            }
        }
    });
	return providers;
});

