import inspect
from functools import wraps
import typing_exe as texe


def execute_annotations(fct):
    pdata = _get_data(fct)

    @wraps(fct)
    def _run(*args, **kwargs):
        args = list(args)   # So that they can be changed

        # Defaults
        for pname in pdata.defaultdata.keys():
            # Don't touch anything that is in args or kwargs
            if pname in kwargs:
                continue
            if pdata.defaultdata.get(pname).get("index") < len(args):   # in args
                continue

            # Handle EarlyReturn
            if isinstance(pdata.defaultdata.get(pname).get("value"), texe.early_return.EarlyReturn):
                return pdata.defaultdata.get(pname).get("value").returns

            # If the default-value is not an instance of EarlyReturn,
            #   add it to args or kwargs (depending on what fits better)
            #   to have it checked below
            if pdata.function_signature.parameters.get(pname).kind == inspect.Parameter.POSITIONAL_ONLY:
                args.append(pdata.defaultdata.get(pname).get("value"))
            else:
                kwargs[pname] = pdata.defaultdata.get(pname).get("value")

        # Args
        for idx, annotation in pdata.arg_annotations.items():
            if idx >= len(args):
                break
            arg = annotation.enforce(
                fct=fct,
                parameter=args[idx],
                parameter_name=pdata.argname_from_index[idx],
                args=args,
                kwargs=kwargs,
                pdata=pdata
            )
            if isinstance(arg, texe.early_return.EarlyReturn):
                return arg.returns
            args[idx] = arg

        # Kwargs
        for pname, parameter in kwargs.items():
            annotation = pdata.kwarg_annotations.get(pname)
            if annotation is not None:
                kwarg = annotation.enforce(
                    fct=fct,
                    parameter=parameter,
                    parameter_name=pname,
                    args=args,
                    kwargs=kwargs,
                    pdata=pdata
                )
                if isinstance(kwarg, texe.early_return.EarlyReturn):
                    return kwarg.returns
                kwargs[pname] = kwarg

        # Return value
        returns = fct(*args, **kwargs)
        if pdata.function_signature.return_annotation != inspect.Parameter.empty \
                and texe.util.is_package_annotation(pdata.function_signature.return_annotation):
            returns = pdata.function_signature.return_annotation.enforce(
                fct=fct,
                parameter=returns,
                parameter_name="return",
                args=args,
                kwargs=kwargs,
                pdata=pdata
            )
            returns = returns.returns if isinstance(returns, texe.early_return.EarlyReturn) else returns

        # Return
        return returns

    return _run


def _get_data(fct):
    signature = inspect.signature(fct)
    arg_annotations = {}
    kwarg_annotations = {}
    defaultdata = {}
    argname_from_index = {}
    index_from_argname = {}

    for i, pname in enumerate(signature.parameters.keys()):
        argname_from_index[i] = pname
        index_from_argname[pname] = i

        # Always save all defaults for CompareWith
        if signature.parameters.get(pname).default != inspect.Parameter.empty:
            defaultdata[pname] = {
                "index": i,
                "value": signature.parameters.get(pname).default
            }

        annotation = signature.parameters.get(pname).annotation

        # Save other data only if it's an annotation
        if not texe.util.is_package_annotation(annotation):
            continue

        # Save arg_annotations and kwarg_annotations
        if not signature.parameters.get(pname).kind == inspect.Parameter.POSITIONAL_ONLY:
            kwarg_annotations[pname] = annotation

        if not signature.parameters.get(pname).kind == inspect.Parameter.KEYWORD_ONLY:
            arg_annotations[i] = annotation

    pdata = texe.parameter_data.ParameterData(
        function_signature=signature,
        arg_annotations=arg_annotations,
        argname_from_index=argname_from_index,
        index_from_argname=index_from_argname,
        kwarg_annotations=kwarg_annotations,
        defaultdata=defaultdata
    )
    return pdata


def cleanup_annotations(fct):
    new_annotations = {}

    for parameter, typehint in fct.__annotations__.items():
        if typehint is None:
            continue
        if texe.util.is_typehint(typehint):
            new_annotations[parameter] = typehint
        elif texe.util.is_package_annotation(typehint) \
                and typehint.typehint is not None:   # if it's not None, parse made sure that it's a typehint!
            new_annotations[parameter] = typehint.typehint

    fct.__annotations__ = new_annotations
    return fct