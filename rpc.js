var result = null

rpc.exports = {
	build: function(apiName, data){
		Java.perform(function () {
			try{
				Hrida = Java.use('me.5alt.hrida')
				hrida = Hrida.$new();
				result = hrida.getInfo().toString()
				console.log(result)
			}catch(e){
				console.log(e)
			}
		});
		return result
	}
}