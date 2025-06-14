import ctypes
from llvmlite import ir, binding
import numpy as np

binding.initialize()
binding.initialize_native_target()
binding.initialize_native_asmprinter()

class LLVMJITCompiler:
    def __init__(self):
        self.target_machine = binding.Target.from_default_triple().create_target_machine()
        self.engine = binding.create_mcjit_compiler(binding.parse_assembly(""), self.target_machine)
        self.mapper_cache = {}

    def compile_ir(self, llvm_ir):
        mod = binding.parse_assembly(llvm_ir)
        mod.verify()
        self.engine.add_module(mod)
        self.engine.finalize_object()
        return mod

    def generate_mapper(self, fields):
        field_names = list(fields.keys())
        func_type = ir.FunctionType(ir.VoidType(), [ir.IntType(64).as_pointer(), ir.IntType(64).as_pointer()])
        module = ir.Module(name="jit_mapper")
        func = ir.Function(module, func_type, name="map_to_instance")
        builder = ir.IRBuilder(func.append_basic_block("entry"))
        instance, data = func.args

        for i, field in enumerate(field_names):
            value = builder.load(builder.gep(data, [ir.Constant(ir.IntType(64), i)]))
            builder.store(value, builder.gep(instance, [ir.Constant(ir.IntType(64), i)]))

        builder.ret_void()
        return self.compile_ir(str(module))

    def get_mapper(self, model_class):
        if model_class not in self.mapper_cache:
            fields = model_class._fields
            field_names = list(fields.keys())
            field_types = [type(value.default) for value in fields.values()]
            mapper = self.generate_mapper(fields)
            func_ptr = self.engine.get_function_address("map_to_instance")
            instance_buffer = np.zeros(len(fields), dtype=np.int64)
            data_buffer = np.zeros(len(fields), dtype=ctypes.c_void_p)
            self.mapper_cache[model_class] = (func_ptr, field_names, field_types, instance_buffer, data_buffer)
        return self.mapper_cache[model_class]

    def map(self, model_class, data):
        func_ptr, field_names, field_types, instance, data_buffer = self.get_mapper(model_class)

        for i, value in enumerate(data):
            if field_types[i] == int:
                data_buffer[i] = ctypes.c_int64(value)
            elif field_types[i] == str:
                data_buffer[i] = ctypes.c_char_p(value.encode("utf-8"))

        ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_void_p))(func_ptr)(
            instance.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            data_buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_void_p))
        )

        return {field_names[i]: instance[i] if field_types[i] == int else data[i] for i in range(len(field_names))}

    def map_batch(self, model_class, rows):
        return [self.map(model_class, row) for row in rows]
