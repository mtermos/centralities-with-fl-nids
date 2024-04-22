class DatasetInfo:
    def __init__(
            self,

            # The name of the dataset.
            name,

            # Column name for source IP addresses in the dataset.
            src_ip_col="Src IP",

            # Column name for destination IP addresses.
            dst_ip_col="Dst IP",

            # Column name for identifying unique network flows.
            flow_id_col="Flow ID",

            # Column name for timestamps of network events.
            timestamp_col="Timestamp",

            # Format of the timestamp data.
            timestamp_format="%d/%m/%Y %I:%M:%S %p",

            # Column name for the label or outcome (e.g., "normal" or "attack").
            label_col="Label",

            # Column name for the class of attack or normal behavior.
            class_col="Attack",

            # Column name for the class of attack or normal behavior.
            class_num_col="Class",

            # Columns to be dropped from the dataset during preprocessing.
            drop_columns=["Flow ID", "Src IP", "Dst IP",
                          "Timestamp", "Src Port", "Dst Port", "Attack", "Class"],

            drop_columns_w_class=["Flow ID", "Src IP", "Dst IP",
                                  "Timestamp", "Src Port", "Dst Port",  "Attack"],

            # Columns to be dropped from the dataset during preprocessing.
            weak_columns=[],

            # Classes with very small availability. To be dropped.
            low_classes=[],
    ):

        self.name = name
        self.src_ip_col = src_ip_col
        self.dst_ip_col = dst_ip_col
        self.flow_id_col = flow_id_col
        self.timestamp_col = timestamp_col
        self.timestamp_format = timestamp_format
        self.label_col = label_col
        self.class_col = class_col
        self.class_num_col = class_num_col
        self.drop_columns = drop_columns
        self.drop_columns_w_class = drop_columns_w_class
        self.weak_columns = weak_columns
        self.low_classes = low_classes


weak_columns = ['Flow Duration', 'Tot Bwd Pkts', 'TotLen Bwd Pkts', 'Fwd Pkt Len Max', 'Fwd Pkt Len Mean', 'Bwd Pkt Len Max', 'Bwd Pkt Len Mean', 'Bwd Pkt Len Std', 'Flow Pkts/s', 'Flow IAT Mean',
                'Flow IAT Max', 'Fwd IAT Mean', 'Bwd IAT Mean', 'Pkt Len Max', 'Pkt Len Mean', 'Pkt Size Avg', 'Fwd Byts/b Avg', 'Fwd Pkts/b Avg', 'Fwd Blk Rate Avg', 'Active Mean', 'Idle Mean']


datasets = [
    # 0
    DatasetInfo("cic_ton_iot",
                weak_columns=weak_columns,
                ),
    # 1
    DatasetInfo("cic_ids_2017",
                timestamp_format="mixed",
                weak_columns=weak_columns,
                low_classes=['Infiltration',
                             'Web Attack � Sql Injection', 'Heartbleed']
                ),
]
