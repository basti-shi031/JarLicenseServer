class ParamUtil(object):
    # 从form中提取参数
    @staticmethod
    def extractParam(form):
        dict = {}
        for field in form.keys():
            field_item = form[field]
            key = field_item.name
            value = field_item.value
            dict[key] = value
        return dict
