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

"""
\begin{RecordType}{\hyperB{IT::Root}{Root}}{}{}{}{Root record of JSON input for Flow123d.}
\KeyItem{\hyperB{Root::problem}{problem}}{abstract type: \Alink{IT::Problem}{Problem}}{\textlangle{\it obligatory }\textrangle}{}{Simulation problem to be solved.}
\KeyItem{\hyperB{Root::pause-after-run}{pause\_after\_run}}{Bool}{false}{}{If true, the program will wait for key press before it terminates.}
\end{RecordType}
"""


def enclose (value=''):
    return "{" + value + "}"


def tag (tag_name, value=''):
    return "\\" + tag_name + "{" + value + "}"


def function (*args):
    return '{' + '}{'.join (args) + '}'


class LatexFormatter (object):
    def __init__ (self, tag_name=None):
        self.tag_name = tag_name

    def open (self):
        return tag ('begin', self.tag_name)

    def close (self):
        return tag ('end', self.tag_name)


class LatexRecordKey (LatexFormatter):
    def __init__ (self):
        super (LatexRecordKey, self).__init__ ('KeyItem')

    # \KeyItem{\hyperB{Root::problem}{problem}}{abstract type: \Alink{IT::Problem}{Problem}}{\textlangle{\it obligatory }\textrangle}{}{Simulation problem to be solved.}
    # \KeyItem{\hyperB{parent.type_name::key}{problem}}{abstract type: \Alink{IT::Problem}{Problem}}{\textlangle{\it obligatory }\textrangle}{}{Simulation problem to be solved.}
    def format (self, record, record_key):
        result = []
        result.append (
            tag ('KeyItem',
                 tag ('hyperB', record.type_name + '::' + record_key.key) + enclose (record_key.key)
            )
        )
        result.append (enclose ('abstract type: ' + tag ('Alink', record_key.type.get_reference ().type_name)))
        return result


class LatexRecord (LatexFormatter):
    def __init__ (self):
        super (LatexRecord, self).__init__ ('RecordType')


    # \begin{RecordType}{\hyperB{IT::Root}{Root}}{}{}{}{Root record of JSON input for Flow123d.}
    # \begin{RecordType}{\hyperB{IT::type_name}{type_name}}{}{}{}{description}
    def format (self, record):
        result = []
        result.append (self.open ())

        # record arguments
        result.append (function (
            tag ('hyperB', 'IT:' + record.type_name),
            record.type_name)
        )
        result.append (enclose ())
        result.append (enclose ())
        result.append (enclose ())
        result.append (enclose (record.description))


        # record keys
        for record_key in record.keys:
            result.extend (LatexRecordKey ().format (record, record_key))
            result.append ('\n')

        result.append (self.close ())
        return result