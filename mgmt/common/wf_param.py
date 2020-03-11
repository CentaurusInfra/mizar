import luigi

class HandlerParam(luigi.Parameter):
	name = ''
	body = dict()
	spec = dict()
	diff = dict()