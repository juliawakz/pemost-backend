import csv
from datetime import datetime

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import path


class ExportActionsMixin:
    """
    Mixin class that provides CSV export and sample CSV download actions
    for Django admin classes.

    Usage:
        class MyModelAdmin(ExportActionsMixin, admin.ModelAdmin):
            actions = ['export_to_csv', 'download_sample_csv']
    """
    change_list_template = 'admin/change_list_with_import.html'

    def export_to_csv(self, request, queryset):
        """
        Export selected model instances to CSV file.
        For foreign keys, exports the string representation instead of ID.
        """
        opts = self.model._meta
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f"attachment;filename={opts.verbose_name}.csv"
        )
        writer = csv.writer(response)

        # Get fields excluding many-to-many, one-to-many, one-to-one
        fields = [
            field
            for field in opts.get_fields()
            if not field.many_to_many
            and not field.one_to_many
            and not field.one_to_one
        ]

        # Write header row with field verbose names
        writer.writerow([field.verbose_name for field in fields])

        # Write data rows
        for obj in queryset:
            data_row = []
            for field in fields:
                value = getattr(obj, field.name)

                # Handle different field types
                if value is None:
                    data_row.append('')
                elif isinstance(value, datetime):
                    value = value.strftime("%d/%m/%Y")
                    data_row.append(value)
                elif field.get_internal_type() == 'ForeignKey':
                    # For foreign keys, use string representation
                    related_obj = getattr(obj, field.name)
                    if related_obj:
                        data_row.append(str(related_obj))
                    else:
                        data_row.append('')
                else:
                    data_row.append(value)
            writer.writerow(data_row)

        return response

    export_to_csv.short_description = "Export selected to CSV"

    def download_sample_csv(self, request, queryset):
        """
        Download a sample CSV template with headers and example data.
        This helps users understand the format needed for bulk imports.
        """
        opts = self.model._meta
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f"attachment;filename={opts.verbose_name}_sample.csv"
        )
        writer = csv.writer(response)

        # Get fields excluding many-to-many, one-to-many, one-to-one
        fields = [
            field
            for field in opts.get_fields()
            if not field.many_to_many
            and not field.one_to_many
            and not field.one_to_one
        ]

        # Write header row
        writer.writerow([field.verbose_name for field in fields])

        # Write a sample data row with field names as placeholders
        sample_row = []
        for field in fields:
            # Provide helpful placeholders based on field type
            if field.name in ["id", "created_at", "updated_at"]:
                sample_row.append("auto-generated")
            elif "date" in field.name.lower():
                sample_row.append("DD/MM/YYYY")
            elif "email" in field.name.lower():
                sample_row.append("example@email.com")
            elif "phone" in field.name.lower():
                sample_row.append("0700000000")
            elif field.get_internal_type() == "BooleanField":
                sample_row.append("True/False")
            elif field.get_internal_type() in [
                "IntegerField",
                "FloatField",
                "DecimalField"
            ]:
                sample_row.append("0")
            elif field.get_internal_type() == "ForeignKey":
                sample_row.append(f"<{field.related_model.__name__} ID>")
            else:
                sample_row.append(f"<{field.name}>")

        writer.writerow(sample_row)

        return response

    download_sample_csv.short_description = "Download Sample CSV Template"

    def get_urls(self):
        """
        Add custom URLs for import and download sample CSV.
        """
        urls = super().get_urls()
        custom_urls = [
            path(
                'download-sample-csv/',
                self.admin_site.admin_view(self.download_sample_csv_view),
                name=f'{self.model._meta.app_label}_{self.model._meta.model_name}_download_sample',
            ),
            path(
                'import-csv/',
                self.admin_site.admin_view(self.import_csv_view),
                name=f'{self.model._meta.app_label}_{self.model._meta.model_name}_import',
            ),
        ]
        return custom_urls + urls

    def download_sample_csv_view(self, request):
        """
        View to download sample CSV without requiring selection.
        """
        opts = self.model._meta
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f"attachment;filename={opts.verbose_name}_sample.csv"
        )
        writer = csv.writer(response)

        # Get fields excluding many-to-many, one-to-many, one-to-one
        fields = [
            field
            for field in opts.get_fields()
            if not field.many_to_many
            and not field.one_to_many
            and not field.one_to_one
        ]

        # Write header row
        writer.writerow([field.verbose_name for field in fields])

        # Write a sample data row with field names as placeholders
        sample_row = []
        for field in fields:
            # Provide helpful placeholders based on field type
            if field.name in ["id", "created_at", "updated_at"]:
                sample_row.append("auto-generated")
            elif "date" in field.name.lower():
                sample_row.append("DD/MM/YYYY")
            elif "email" in field.name.lower():
                sample_row.append("example@email.com")
            elif "phone" in field.name.lower():
                sample_row.append("0700000000")
            elif field.get_internal_type() == "BooleanField":
                sample_row.append("True/False")
            elif field.get_internal_type() in [
                "IntegerField",
                "FloatField",
                "DecimalField"
            ]:
                sample_row.append("0")
            elif field.get_internal_type() == "ForeignKey":
                sample_row.append(f"<{field.related_model.__name__} ID>")
            else:
                sample_row.append(f"<{field.name}>")

        writer.writerow(sample_row)

        return response

    def import_csv_view(self, request):
        """
        View to handle CSV file upload and import.
        """
        if request.method == "POST" and request.FILES.get('csv_file'):
            csv_file = request.FILES['csv_file']

            # Check if file is CSV
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Please upload a valid CSV file.')
                return redirect('..')

            try:
                # Decode the file
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)

                created_count = 0
                updated_count = 0
                error_count = 0
                errors = []

                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Process the row
                        result = self.process_csv_row(row)
                        if result == 'created':
                            created_count += 1
                        elif result == 'updated':
                            updated_count += 1
                    except Exception as e:
                        error_count += 1
                        errors.append(f"Row {row_num}: {str(e)}")
                        if len(errors) >= 10:  # Limit error messages
                            errors.append(
                                f"... and {error_count - 10} more errors"
                            )
                            break

                # Display results
                if created_count > 0:
                    messages.success(
                        request,
                        f'Successfully created {created_count} records.'
                    )
                if updated_count > 0:
                    messages.success(
                        request,
                        f'Successfully updated {updated_count} records.'
                    )
                if error_count > 0:
                    messages.warning(
                        request,
                        f'{error_count} rows failed. Errors: {"; ".join(errors)}'
                    )

                return redirect('..')

            except Exception as e:
                messages.error(
                    request,
                    f'Error processing CSV file: {str(e)}'
                )
                return redirect('..')

        # Render upload form
        context = {
            'title': f'Import {self.model._meta.verbose_name_plural}',
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request),
        }
        return render(
            request,
            'admin/import_csv.html',
            context
        )

    def process_csv_row(self, row):
        """
        Process a single CSV row. Override this method in subclasses
        for custom import logic.

        Returns: 'created' or 'updated' or raises an exception
        """
        # Default implementation - create new instance
        # Subclasses should override this for more sophisticated logic
        instance = self.model()
        for field_name, value in row.items():
            if hasattr(instance, field_name):
                setattr(instance, field_name, value)
        instance.save()
        return 'created'

    def changelist_view(self, request, extra_context=None):
        """
        Add import and download buttons to changelist view.
        """
        extra_context = extra_context or {}
        extra_context['has_import_permission'] = self.has_add_permission(request)
        extra_context['import_url'] = f'import-csv/'
        extra_context['download_sample_url'] = f'download-sample-csv/'
        return super().changelist_view(request, extra_context=extra_context)
