import 'package:flutter/material.dart';

import '../../../../constants.dart';

class CentimetersSizeTable extends StatelessWidget {
  const CentimetersSizeTable({super.key});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: ClipRRect(
        borderRadius:
            const BorderRadius.all(Radius.circular(defaultBorderRadious)),
        child: DataTable(
          border: TableBorder(
            verticalInside: BorderSide(
                color: Theme.of(context).brightness == Brightness.light
                    ? Colors.black12
                    : Colors.white10),
          ),
          columns: const <DataColumn>[
            DataColumn(
                label: Expanded(
              child: Text(
                'General Size',
                maxLines: 2,
              ),
            )),
            DataColumn(
                label: Expanded(
              child: Text('US Hat size'),
            )),
            DataColumn(
              label: Expanded(
                child: Text('Head Measurement'),
              ),
            ),
          ],
          rows: const <DataRow>[
            DataRow(
              cells: <DataCell>[
                DataCell(Text('S-M')),
                DataCell(Text('S-M')),
                DataCell(Text('21 7/8 - 22')),
              ],
            ),
            DataRow(
              cells: <DataCell>[
                DataCell(Text('L-XL')),
                DataCell(Text('L-XL')),
                DataCell(Text('22 5/8 - 23')),
              ],
            ),
          ],
        ),
      ),
    );
  }
}