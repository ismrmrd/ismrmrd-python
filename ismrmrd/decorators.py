import copy 


class  expose_header_fields:
    def __init__(self,header_cls) -> None:
        self.header_cls = header_cls

    def __call__(self,cls):
        def create_getter_and_setter(field):
            if field in cls._readonly:
                def getter(self):
                    return copy.copy(self._head.__getattribute__(field))
                def setter(self,val):
                    raise AttributeError(field+ " is read-only. Use resize instead.")
            else:
                def getter(self):
                    return self._head.__getattribute__(field)
                def setter(self, val):
                    self._head.__setattr__(field, val)
            
            return getter,setter
    
        ignore_list = cls._ignore if hasattr(cls,"_ignore") else []
    
        for (field, _) in self.header_cls._fields_:
            if field in ignore_list:
                continue 
            try:
                g = '__get_' + field
                s = '__set_' + field
    
                getter,setter = create_getter_and_setter(field)
                setattr(cls, g, getter)
                setattr(cls, s, setter)
                p = property(getattr(cls, g), getattr(cls, s))
                setattr(cls, field, p)
            except TypeError:
                # e.g. if key is an `int`, skip it
                pass
    
        return cls 

