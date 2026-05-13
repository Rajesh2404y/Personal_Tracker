import csv
import io
from decimal import Decimal
from django.http import HttpResponse
from django.db.models import Sum
from apps.transactions.models import Transaction


class ReportGenerator:
    def __init__(self, user, date_from, date_to):
        self.user = user
        self.date_from = date_from
        self.date_to = date_to
        self.transactions = Transaction.objects.filter(
            user=user, date__gte=date_from, date__lte=date_to
        ).select_related('category').order_by('date')

    def generate_csv(self):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Date', 'Type', 'Category', 'Description', 'Amount', 'Tags'])
        for txn in self.transactions:
            writer.writerow([
                txn.date, txn.transaction_type,
                txn.category.name if txn.category else '',
                txn.description, txn.amount, txn.tags
            ])
        totals = self.transactions.values('transaction_type').annotate(total=Sum('amount'))
        writer.writerow([])
        writer.writerow(['Summary'])
        for row in totals:
            writer.writerow([row['transaction_type'].title(), '', '', 'Total', row['total'], ''])
        return output.getvalue()

    def generate_excel(self):
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Transactions'

        headers = ['Date', 'Type', 'Category', 'Description', 'Amount', 'Tags']
        header_fill = PatternFill(start_color='6366F1', end_color='6366F1', fill_type='solid')
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True, color='FFFFFF')
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')

        for row_idx, txn in enumerate(self.transactions, 2):
            ws.cell(row=row_idx, column=1, value=str(txn.date))
            ws.cell(row=row_idx, column=2, value=txn.transaction_type.title())
            ws.cell(row=row_idx, column=3, value=txn.category.name if txn.category else '')
            ws.cell(row=row_idx, column=4, value=txn.description)
            ws.cell(row=row_idx, column=5, value=float(txn.amount))
            ws.cell(row=row_idx, column=6, value=txn.tags)

        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width = 18

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output

    def get_summary(self):
        income = self.transactions.filter(transaction_type='income').aggregate(t=Sum('amount'))['t'] or Decimal('0')
        expense = self.transactions.filter(transaction_type='expense').aggregate(t=Sum('amount'))['t'] or Decimal('0')
        by_category = list(
            self.transactions.values('category__name', 'transaction_type')
            .annotate(total=Sum('amount'))
            .order_by('-total')
        )
        return {'income': income, 'expense': expense, 'net': income - expense, 'by_category': by_category}
