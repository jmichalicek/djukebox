import pysox
import os

def convert_file_to_ogg(filename):
    # TODO: make sure the file isn't already an ogg

    directory, name = os.path.split(filename)
    name, extension = os.path.splitext(name)
    target_filename = os.path.join(directory, '%s.ogg' %name)

    writer = pysox.CSoxApp(filename, target_filename)
    writer.flow()

    return target_filename
    # The above is creating ogg files which firefox refuses to play properly, although Opera plays them.
    # Perhaps we can fix it by tweaking settings and doing it more manually like below

    #source_file = pysox.CSoxStream(filename)
    #out_file = pysox.CSoxStream(target_filename, 'w', source_file.get_signal(), fileType='ogg')
    #chain = pysox.CEffectsChain(source_file, out_file)
    #chain.flow_effects()

    #out_file.close()
    #source_file.close()

    #return target_filename
