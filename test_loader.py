import pkg_resources

named_objects = dict()
print("hook2")
for ep in pkg_resources.iter_entry_points(group='genice_format_hook2'):
    print(ep.name)
    named_objects[ep.name] = ep.load()
    # named_objects[ep.name]()

print("hook4")
for ep in pkg_resources.iter_entry_points(group='genice_format_hook4'):
    print(ep.name)
    named_objects[ep.name] = ep.load()
    # named_objects[ep.name]()

#ep = pkg_resources.get_entry_info(group='genice_format_hook2', name='svg', dist="")
#print(ep.name)
