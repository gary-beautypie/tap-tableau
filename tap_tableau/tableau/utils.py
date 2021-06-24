import singer
import tableauserverclient as TSC


def format_datetime(dt):
    if dt is not None:
        return singer.utils.strftime(dt)
    return None


def get_start_date_filter(start_date):
    req_option = TSC.RequestOptions()
    req_option.sort.add(
        TSC.Sort(
            TSC.RequestOptions.Field.UpdatedAt,
            TSC.RequestOptions.Direction.Asc
        )
    )
    req_option.filter.add(
        TSC.Filter(
            TSC.RequestOptions.Field.UpdatedAt,
            TSC.RequestOptions.Operator.GreaterThanOrEqual,
            format_datetime(start_date)
        )
    )
    return req_option
