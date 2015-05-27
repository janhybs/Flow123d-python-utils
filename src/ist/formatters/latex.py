# encoding: utf-8
# author:   Jan Hybs


"""
\begin{RecordType}{\hyperB{IT::SequentialCoupling}{SequentialCoupling}}{\Alink{IT::Problem}{Problem}}{}{}{Record with data for a general sequential coupling.
}
\KeyItem{\hyperB{SequentialCoupling::TYPE}{TYPE}}{selection: Problem\_TYPE\_selection}{SequentialCoupling}{}{Sub-record selection.}
\KeyItem{\hyperB{SequentialCoupling::description}{description}}{String (generic)}{\textlangle{\it optional }\textrangle}{}{Short description of the solved problem.\\Is displayed in the main log, and possibly in other text output files.}
\KeyItem{\hyperB{SequentialCoupling::mesh}{mesh}}{record: \Alink{IT::Mesh}{Mesh}}{\textlangle{\it obligatory }\textrangle}{}{Computational mesh common to all equations.}
\KeyItem{\hyperB{SequentialCoupling::time}{time}}{record: \Alink{IT::TimeGovernor}{TimeGovernor}}{\textlangle{\it optional }\textrangle}{}{Simulation time frame and time step.}
\KeyItem{\hyperB{SequentialCoupling::primary-equation}{primary\_equation}}{abstract type: \Alink{IT::DarcyFlowMH}{DarcyFlowMH}}{\textlangle{\it obligatory }\textrangle}{}{Primary equation, have all data given.}
\KeyItem{\hyperB{SequentialCoupling::secondary-equation}{secondary\_equation}}{abstract type: \Alink{IT::Transport}{Transport}}{\textlangle{\it optional }\textrangle}{}{The equation that depends (the velocity field) on the result of the primary equation.}
\end{RecordType}
"""
from ist.nodes import Bool, AbstractRecord, Selection

"""
\begin{RecordType}{\hyperB{IT::Root}{Root}}{}{}{}{Root record of JSON input for Flow123d.}
\KeyItem{\hyperB{Root::problem}{problem}}{abstract type: \Alink{IT::Problem}{Problem}}{\textlangle{\it obligatory }\textrangle}{}{Simulation problem to be solved.}
\KeyItem{\hyperB{Root::pause-after-run}{pause\_after\_run}}{Bool}{false}{}{If true, the program will wait for key press before it terminates.}
\end{RecordType}
"""


def function (*args): return '{' + '}{'.join (args) + '}'


slash = '\\'

tag = lambda t, v: "\\" + t + "{" + v + "}"
enclose = lambda v: "{" + v + "}"
hyperB = lambda v: "\\hyperB{" + v + "}"
Alink = lambda v: "\\Alink{" + v + "}"
it = lambda v: 'IT::' + v
sub = lambda a, b: a + '::' + b
u2d = lambda v: v.replace ('_', '-')
u2s = lambda v: v.replace ('_', '\\_')

double_tag = lambda t, s, v: "{\\" + t + "{" + s + u2d (v) + "}{" + u2s (v) + "}}"
double_hyperB = lambda s, v: "{\\hyperB{" + s + u2d (v) + "}{" + u2s (v) + "}}"
desc = lambda v: v.strip ().replace ('\\n', '\\\\')


class LatexItemFormatter (object):
    def __init__ (self, tag_name=None):
        self.tag_name = tag_name

    def open (self):
        return tag ('begin', self.tag_name)

    def close (self):
        return tag ('end', self.tag_name)


'''
{
  "id": "f9756fb2f66076a1",
  "input_type": "Selection",
  "name": "PartTool",
  "full_name": "PartTool",
  "description": "Select the partitioning tool to use.",
  "values": [
     {
        "name": "PETSc",
        "description": "Use PETSc interface to various partitioning tools."
     },
     {
        "name": "METIS",
        "description": "Use direct interface to Metis."
     }
  ]
}

\begin{SelectionType}{\hyperB{IT::PartTool}{PartTool}}{Select the partitioning tool to use.}
\KeyItem{PETSc}{Use PETSc interface to various partitioning tools.}
\KeyItem{METIS}{Use direct interface to Metis.}
\end{SelectionType}
'''


class LatexSelection (LatexItemFormatter):
    def __init__ (self):
        super (LatexRecordKey, self).__init__ ('SelectionType')


    def format (self, selection, record_key=None, record=None):
        if record_key is None and record is None:
            result = []
            result.append (self.open ())
            result.append ()


'''
{
    "key": "TYPE",
    "description": "Sub-record selection.",
    "default": {
        "type": "value at declaration",
        "value": "SequentialCoupling"
    },
    "type": "b0bf265898e2625b"
}

\KeyItem{\hyperB{SequentialCoupling::TYPE}{TYPE}}{selection: Problem\_TYPE\_selection}{SequentialCoupling}{}{Sub-record selection.}
'''


class LatexRecordKey (LatexItemFormatter):
    def __init__ (self):
        super (LatexRecordKey, self).__init__ ('KeyItem')

    def format (self, record_key, record):
        result = list ()
        reference = record_key.type.get_reference ()

        # record key head is same for every type
        # \KeyItem{\hyperB{Root::problem}{problem}}
        result.append (slash + 'KeyItem')
        result.append (
            double_hyperB (record.type_name + '::', record_key.key)
        )

        try:
            fmt = LatexFormatter.get_formatter_for (reference)
        except Exception as e:
            fmt = None
            print e

        if fmt:
            result.extend (fmt.format_as_child (reference, record_key, record))
            result.append (enclose (''))
            result.append (enclose (desc (record_key.description)))
        else:
            result.append (' <<Missing formatter for {}>>'.format (type (reference)))
        return result


'''
{
  "id": "1b711c7cb758740",
  "input_type": "AbstractRecord",
  "name": "Problem",
  "full_name": "Problem",
  "description": "The root record of description of particular the problem to solve.",
  "implementations": [
     "81a9cc0d6917a75"
  ]
}

\begin{AbstractType}{\hyperB{IT::Problem}{Problem}}{}{}{The root record of description of particular the problem to solve.}
\Descendant{\Alink{IT::SequentialCoupling}{SequentialCoupling}}
\end{AbstractType}
'''


class LatexAbstractRecord (LatexItemFormatter):
    def __init__ (self):
        super (LatexAbstractRecord, self).__init__ ('AbstractType')

    def format_as_child (self, abstract_record, record_key, record):
        result = list ()
        result.append (
            enclose ('abstract type: ' +
                     Alink (it (abstract_record.name)) +
                     enclose (abstract_record.name)
            )
        )
        result.append (
            enclose ('\\textlangle' +
                     enclose ('\\it ' + record_key.default.type + ' ') +
                     '\\textrangle'
            )
        )
        return result

    def format (self, abstract_record):
        result = list ()
        result.append (self.open ())
        result.append (double_hyperB ('IT::', abstract_record.name))
        result.append (enclose (''))
        result.append (enclose (''))
        result.append (enclose (abstract_record.description))

        for descendant in abstract_record.implementations:
            result.append ('\n')
            result.append (slash + 'Descendant')
            result.append (double_tag ('Alink', 'IT::', descendant.get_reference ().type_name))

        result.append ('\n')
        result.append (self.close ())
        return result


'''
{
  "id": "29b5533100b6f60f",
  "input_type": "String",
  "name": "String",
  "full_name": "String"
}

unknown root format so far
'''


class LatexString (LatexItemFormatter):
    def __init__ (self):
        super (LatexString, self).__init__ ('String')


    # {String (generic)}{\textlangle{\it optional }\textrangle}{}{Short description of the solved problem.\\Is displayed in the main log, and possibly in other text output files.}
    def format_as_child (self, self_string, record_key, record):
        result = list ()
        result.append (enclose (self_string.name + ' (generic)'))
        result.append (
            enclose ('\\textlangle' +
                     enclose ('\\it ' + record_key.default.type + ' ') +
                     '\\textrangle'
            )
        )
        return result


'''
{
  "id": "81a9cc0d6917a75",
  "input_type": "Record",
  "type_name": "SequentialCoupling",
  "type_full_name": "SequentialCoupling:Problem",
  "description": "Record with data for a general sequential coupling.\n",
  "implements": [
     "1b711c7cb758740"
  ],
  "keys": [
     {
        "key": "TYPE",
        "description": "Sub-record selection.",
        "default": {
           "type": "value at declaration",
           "value": "SequentialCoupling"
        },
        "type": "b0bf265898e2625b"
     },
     {
        "key": "description",
        "description": "Short description of the solved problem.\nIs displayed in the main log, and possibly in other text output files.",
        "default": {
           "type": "optional",
           "value": "OPTIONAL"
        },
        "type": "29b5533100b6f60f"
     },
     {
        "key": "mesh",
        "description": "Computational mesh common to all equations.",
        "default": {
           "type": "obligatory",
           "value": "OBLIGATORY"
        },
        "type": "c57e1ac33a446313"
     },
     {
        "key": "time",
        "description": "Simulation time frame and time step.",
        "default": {
           "type": "optional",
           "value": "OPTIONAL"
        },
        "type": "d8574f6af69c7e1f"
     },
     {
        "key": "primary_equation",
        "description": "Primary equation, have all data given.",
        "default": {
           "type": "obligatory",
           "value": "OBLIGATORY"
        },
        "type": "89b3f40b6e805da8"
     },
     {
        "key": "secondary_equation",
        "description": "The equation that depends (the velocity field) on the result of the primary equation.",
        "default": {
           "type": "optional",
           "value": "OPTIONAL"
        },
        "type": "ba303ae783dcf903"
     }
  ]
}
\begin{RecordType}{\hyperB{IT::SequentialCoupling}{SequentialCoupling}}{\Alink{IT::Problem}{Problem}}{}{}{Record with data for a general sequential coupling.}
\KeyItem{\hyperB{SequentialCoupling::TYPE}{TYPE}}{selection: Problem\_TYPE\_selection}{SequentialCoupling}{}{Sub-record selection.}
\KeyItem{\hyperB{SequentialCoupling::description}{description}}{String (generic)}{\textlangle{\it optional }\textrangle}{}{Short description of the solved problem.\\Is displayed in the main log, and possibly in other text output files.}
\KeyItem{\hyperB{SequentialCoupling::mesh}{mesh}}{record: \Alink{IT::Mesh}{Mesh}}{\textlangle{\it obligatory }\textrangle}{}{Computational mesh common to all equations.}
\KeyItem{\hyperB{SequentialCoupling::time}{time}}{record: \Alink{IT::TimeGovernor}{TimeGovernor}}{\textlangle{\it optional }\textrangle}{}{Simulation time frame and time step.}
\KeyItem{\hyperB{SequentialCoupling::primary-equation}{primary\_equation}}{abstract type: \Alink{IT::DarcyFlowMH}{DarcyFlowMH}}{\textlangle{\it obligatory }\textrangle}{}{Primary equation, have all data given.}
\KeyItem{\hyperB{SequentialCoupling::secondary-equation}{secondary\_equation}}{abstract type: \Alink{IT::Transport}{Transport}}{\textlangle{\it optional }\textrangle}{}{The equation that depends (the velocity field) on the result of the primary equation.}
\end{RecordType}
'''
# TODO textrangle textlangle

class LatexRecord (LatexItemFormatter):
    def __init__ (self):
        super (LatexRecord, self).__init__ ('RecordType')


    # {record: \Alink{IT::Mesh}{Mesh}}{\textlangle{\it obligatory }\textrangle}{}{Computational mesh common to all equations.}
    def format_as_child (self, self_record, record_key, record):
        result = list ()
        result.append (enclose (
            'record: ' +
            Alink (it (u2d (self_record.type_name))) +
            enclose (u2s (self_record.type_name))
        ))
        result.append (
            enclose ('\\textlangle' +
                     enclose ('\\it ' + record_key.default.type + ' ') +
                     '\\textrangle'
            )
        )
        return result

    # \begin{RecordType}{\hyperB{IT::type_name}{type_name}}{}{}{}{description}
    def format (self, record):
        result = list ()
        result.append (self.open ())

        reference_list = record.implements

        # record arguments
        result.append (double_hyperB ('IT::', record.type_name))
        # link to implements
        if reference_list:
            for reference in reference_list:
                result.append (double_tag ('Alink', 'IT::', reference.get_reference ().name))  # link to implements
        else:
            result.append (enclose (''))

        # unknown
        result.append (enclose (''))
        # unknown
        result.append (enclose (''))
        # description
        result.append (enclose (record.description))

        # record keys
        for record_key in record.keys:
            try:
                fmt = LatexFormatter.get_formatter_for (record_key)

                result.append ('\n')
                result.extend (fmt.format (record_key, record))
            except Exception as e:
                print e
                continue

        result.append ('\n')
        result.append (self.close ())
        return result


class LatexFormatter (object):
    formatters = {
        'Record': LatexRecord,
        'RecordKey': LatexRecordKey,
        'AbstractRecord': LatexAbstractRecord,
        'String': LatexString
    }

    @staticmethod
    def format (items):
        result = list ()

        for item in items:
            try:
                fmt = LatexFormatter.get_formatter_for (item)
            except Exception as e:
                raise e
                continue

            result.extend (fmt.format (item))

        return result

    @staticmethod
    def get_formatter_for (o):
        cls = LatexFormatter.formatters.get (o.__class__.__name__, None)
        if cls is None:
            raise Exception ('no formatter found for {}'.format (o.__class__.__name__))
        return cls ()