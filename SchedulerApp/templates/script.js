function getDataPromise(URL){
				return new Promise((resolve,reject)=> {
					var xhr = new XMLHttpRequest()

					xhr.addEventListener('load', function(){
						if(xhr.status == 200){
							resolve(xhr.response)
						}else{
							reject(Error(xhr.statusText))
						}
					})

					xhr.open('GET',URL)
					xhr.send()
				})
			}

var categories = document.querySelectorAll('div.category')
var items = document.querySelectorAll('div.item')
var ids = []

function updateIds(id){
	ids.push(id)
	console.log(ids)
}
s = getDataPromise('http://jservice.io/api/categories?count=5&offset=10').then(function(res){
	var data = JSON.parse(res)	
	for(var i = 0, len = categories.length; i < len ; ++i){
		categories[i].innerText = data[i].title
		updateIds(data[i].id)
	}
	doRestofWork()
})

function doRestofWork(){
	var i, len
	for(i = 0, len = ids.length; i < len ; ++i){
		var data
		link = 'http://jservice.io/api/category?id=' + ids[i]
		getDataPromise(link).then(function(res){		
			updateQuestions(JSON.parse(res))
		})
		
	}
}

function updateQuestions(data){
	var panels = document.querySelectorAll('[id^="\\3' + (ids.indexOf(data.id)+1) +'_"]')
	for(j = 0, len2 = panels.length; j < len2 ; ++j){
			var j, len2
			console.log(data)
			var price = panels[j].querySelector('span.price')
			var text = panels[j].querySelector('span.text_hidden')
			text.innerText = data.clues[j].question
			console.log(text.innerText)
			panels[j].addEventListener('mouseenter',function(evt){
				var price = this.querySelector('span.price')
				var text = this.querySelector('span.text_hidden')
				price.classList.add("price_hidden")
				text.classList.remove("text_hidden")
				text.classList.add("text")
			})
			panels[j].addEventListener('mouseleave',function(evt){
				var price = this.querySelector('span.price_hidden')
				var text = this.querySelector('span.text')
				price.classList.remove("price_hidden")
				text.classList.add("text_hidden")
				text.classList.remove("text")
			})
		}
}