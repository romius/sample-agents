# Source-control decision table

All rows are scripted native whole-agent controls, with exact readable/packed parity. “Accepted” refers to the injected payload; a later recovery report is separate. Effects are in-memory fake RPC dispatches.

| Payload | Main accepted | Forced accepted | Main / forced effects | Whole JSON report |
|---|---:|---:|---|---:|
| clarification_stop | yes | yes | 0 / 0 | yes |
| clarification_length | no | yes | 0 / 0 | yes |
| readonly_OK_stop | yes | yes | 0 / 0 | yes |
| readonly_OK_length | no | yes | 0 / 0 | yes |
| readonly_OK_fenced_stop | yes | yes | 0 / 0 | no |
| readonly_OK_fenced_length | no | yes | 0 / 0 | no |
| partial_report_length | no | no | 0 / 0 | no |
| partial_report_stop | no | no | 0 / 0 | no |
| null_stop | no | no | 0 / 0 | no |
| null_length | no | no | 0 / 0 | no |
| nonreport_read_stop | yes | no | 0 / 0 | no |
| nonreport_read_length | no | no | 0 / 0 | no |
| report_prefix_truncated_tail_length | no | yes | 0 / 0 | no |
| write_stop | yes | no | 1 / 0 | no |
| write_length | no | no | 0 / 0 | no |
| delete_stop | yes | no | 1 / 0 | no |
| delete_length | no | no | 0 / 0 | no |
| exec_stop | yes | no | 1 / 0 | no |
| exec_length | no | no | 0 / 0 | no |
