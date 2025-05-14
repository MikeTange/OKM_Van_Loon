from tkinter import filedialog, messagebox, ttk
from bom_pre_processing import *
from data_validation import *
from product_master import *
from typing import Literal
from data_loading import *
from save_output import *
from processing import *
from parameters import *
import tkinter as tk
import threading
import queue
import os


class AsyncTaskRunner:
    """ 
    Handler for heavy workloads being passed on to a background thread

    The handler takes care of the creation of a background thread,
    passing intermediate progress data from the function being called to a progress bar,
    and calling an on_complete function for handling the return to the main thread.
    """

    def __init__(self, 
                 root : tk.Tk, 
                 task_fn : Callable, 
                 args : tuple=(), 
                 progress_var : tk.DoubleVar=None, 
                 progress_bar: ttk.Progressbar=None, 
                 on_complete : Callable=None):
        """ 
        Initialise an AsyncTaskRunner 

        Parameters
        ----------
        root : tk.Tk
            the main GUI window
        task:fn : Callable
            the function to run on a separate thread
        args : tuple
            the function arguments
        progress_var : tk.DoubleVar
            the variable (value) linked to the progress bar
        progress_bar : ttk.Progressbar
            the progress bar meant to track the execution of the task
        on_complete : Callable
            the function to call upon completion of the task
        """

        self.root = root
        self.task_fn = task_fn
        self.args = args
        self.progress_var = progress_var or tk.DoubleVar()
        self.progress_bar = progress_bar
        self.on_complete = on_complete
        self.progress_queue = queue.Queue(maxsize=100)
        self.result_queue = queue.Queue(maxsize=10)
        self.thread = None

        if self.progress_bar:
            self.progress_bar.config(variable=self.progress_var, maximum=100)

    def start(self):
        """ Start the task """

        self.thread = threading.Thread(target=self._run_task)
        self.thread.start()
        self._poll_queue()

    def _run_task(self):
        """ Run the task """

        result = self.task_fn(*self.args, progress_queue=self.progress_queue)
        self.result_queue.put(result)
        self.progress_queue.put("done")

    def _poll_queue(self):
        """ Poll the progress & result queues to send updates to the main thread """
        try:
            while True:
                val = self.progress_queue.get_nowait()
                if val == "done":
                    if self.on_complete:
                        result = self.result_queue.get_nowait()
                        self.on_complete(result)
                    return
                self.progress_var.set(val)
                if self.progress_bar:
                    self.progress_bar.update_idletasks()
        except queue.Empty:
            self.root.after(100, self._poll_queue)


class OKM_processing:
    """ OKM Processing App """


    def __init__(self, root):
        """ Initialise the GUI """

        self.root = root
        self.root.title("OKM Processing")

        # Variable to store input file paths
        self.input_files = {'BOM': None,
                            'Prijslijst': None,
                            'Waste lijst': None,
                            'Actieve lijst': None}
        
        # Variable to store input Excel sheets
        self.selected_sheets = {'BOM': None,
                                'Prijslijst': None,
                                'Waste lijst': None,
                                'Actieve lijst': None}
        
        # Variable to store selected columns
        self.selected_columns = {'Prijslijst': None, 
                                 'Actieve lijst': None}

        # Variable to store datasets
        self.datasets = {}

        # Variables for Excel sheets selection dropdowns
        self.sheet_options = {'BOM': None,
                              'Prijslijst': None,
                              'Waste lijst': None,
                              'Actieve lijst': None}
        self.sheet_dropdowns = {'BOM': None,
                                'Prijslijst': None,
                                'Waste lijst': None,
                                'Actieve lijst': None}

        # Variables for column selection dropdowns
        self.column_options = {'Prijslijst': None, 
                               'Actieve lijst': None}
        self.column_dropdowns = {'Prijslijst': None, 
                                 'Actieve lijst': None}
        
        # Task handlers for multithreading
        self.task_handlers = {}

        # Build the GUI
        self.build_gui()


    def build_gui(self):
        """ 
        Build the GUI

        The GUI consists of a number of widgets:
        - Input files: to select the input Excel files, and sheets
        - Data loading: to run data loading, with a progress bar
        - Select columns: to select the relevant columns for processing
        - Processing: to run data validation and processing, with progress bars
        - Status area: to display status messages to the user
        """
        
        # Progress bars
        self.progressbars = {'load': None,
                             'validate': None,
                             'process': None}

        # Input files selection
        self.file_frame = tk.LabelFrame(self.root, text="Input Files", padx=10, pady=10)
        self.file_frame.pack(padx=10, pady=10, fill="x")

        self.file_labels = []

        i = 0
        for key in self.input_files.keys(): # TODO - test with more keys than 4
            # Excel file selection
            btn = tk.Button(self.file_frame, text=f"Select Input File {key}", command=lambda idx=i, key=key: self.select_input_file(key=key, index=idx))
            btn.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
            label = tk.Label(self.file_frame, text="No file selected", anchor="w")
            label.grid(row=i, column=1, padx=5, pady=5, sticky="w")
            self.file_labels.append(label)

            # Excel sheet selection
            self.sheet_labels = []

            dropdown = ttk.Combobox(self.file_frame, state="disabled")
            dropdown.grid(row=i, column=2, padx=5, pady=5, sticky="ew")
            label = tk.Label(self.file_frame, text="Excel sheet", anchor="w")
            label.grid(row=i, column=3, padx=5, pady=5, sticky="w")
            self.sheet_labels.append(label)
            self.sheet_dropdowns[key] = dropdown
            
            i += 1
        
        # Data loading
        self.loading_frame = tk.LabelFrame(self.root, text="Load Data", padx=10, pady=10)
        self.loading_frame.pack(padx=10, pady=10, fill="x")

        self.loading_label = tk.Label(self.loading_frame)
        self.loading_label.pack()

        self.load_button = tk.Button(self.loading_label, text="Load Data", command=self.load_data)
        self.load_button.grid(row=0, column=0, padx=10)
        
        load_progress = ttk.Progressbar(self.loading_label, mode='determinate')
        load_progress.grid(row=0, column=1)
        self.progressbars['load'] = load_progress

        # Column Selection
        column_frame = tk.LabelFrame(self.root, text="Select Columns", padx=10, pady=10)
        column_frame.pack(padx=10, pady=10, fill="x")

        self.column_labels = []

        i = 0 
        for key in self.selected_columns.keys():
            label = tk.Label(column_frame, text=f"Select {key}")
            label.grid(row=i, column=0, padx=5, pady=5, sticky="w")
            dropdown = ttk.Combobox(column_frame, state="disabled")
            dropdown.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            self.column_labels.append(label)
            self.column_dropdowns[key] = dropdown
            i += 1

        # Processing
        self.processing_frame = tk.LabelFrame(self.root, text="Processing", padx=10, pady=10)
        self.processing_frame.pack(padx=10, pady=10, fill="x")

        # Data Validation
        self.validate_label = tk.Label(self.processing_frame)
        self.validate_label.pack()

        self.validate_button = tk.Button(self.validate_label, text="Validate Data", command=self.run_data_validation, state="disabled")
        self.validate_button.grid(row=0, column=0, padx=10)

        validate_progress = ttk.Progressbar(self.validate_label, mode='determinate')
        validate_progress.grid(row=0, column=1)
        self.progressbars['validate'] = validate_progress

        # Data Processing
        self.process_label = tk.Label(self.processing_frame)
        self.process_label.pack()

        self.process_button = tk.Button(self.process_label, text="Process Data", command=self.run_processing, state="disabled")
        self.process_button.grid(row=0, column=0, padx=10)

        process_progress = ttk.Progressbar(self.process_label, mode='determinate')
        process_progress.grid(row=0, column=1)
        self.progressbars['process'] = process_progress

        # Status Area
        status_frame = tk.LabelFrame(self.root, text="Status", padx=10, pady=10)
        status_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.status_text = tk.Text(status_frame, height=10, state="disabled")
        self.status_text.pack(fill="both", expand=True)


    def select_input_file(self, key : str, index : int):
        """
        Selector for the input files.

        Uses tkinter's filedialog to prompt the user to select input files

        Parameters
        ----------
        key : str
            the key representing which input file is being selected
        index : int
            the index of the input file selector within the widget
        """
        
        filepath = filedialog.askopenfilename(title="Select Excel File", filetypes=[("Excel files", "*.xlsx *.xls")])
        if filepath:
            self.input_files[key] = filepath
            self.file_labels[index].config(text=os.path.basename(filepath))
            self.update_status(f"Selected Input File {key}: {filepath}")

            self.sheet_options[key] = pd.ExcelFile(self.input_files[key]).sheet_names
            sheet_dropdown = self.sheet_dropdowns[key]
            sheet_dropdown.config(state="readonly", values=self.sheet_options[key])
            sheet_dropdown.set('')  # Clear selection - TODO double check this for desirability


    @staticmethod
    def load_all_data(input_files : dict, selected_sheets : dict, progress_queue : queue.Queue=None):
        """
        Load all selected input data from Excel files. 
        
        This method assumes the keys of input_files and selected_sheets are the input_file_type strings as well.

        Parameters
        ----------
        input_files : dict
            dictionary containing the input file paths
        selected_sheets : dict
            dictionary containing the Excel sheets for each input file
        progress_queue : queue.Queue
            the queue used for updating the progress bar

        returns
        -------
        results : dict
            dictionary containing the loaded datasets
        """

        if progress_queue:
                progress_queue.put(5)

        results = {}
        total = len([k for k in selected_sheets if selected_sheets[k]]) + 0.001

        for i, input_type in enumerate(selected_sheets):
            file_path = input_files.get(input_type)
            sheet_name = selected_sheets.get(input_type)

            if not file_path or not sheet_name:
                continue  # skip incomplete selections

            data = load_input_file(file_path, sheet_name, input_file_type=input_type)
            results[input_type] = data

            if progress_queue:
                progress_queue.put((i + 1) / total * 100)

        if progress_queue:
            progress_queue.put('done')

        return results


    def load_data(self):
        """ Start threaded data loading task """

        # Validate selections
        file_warns = [k for k, v in self.input_files.items() if v is None]
        sheet_warns = [k for k in self.selected_sheets if not self.sheet_dropdowns[k].get()]

        if file_warns or sheet_warns:
            messagebox.showwarning("Missing Selection",
                f"{'Please select files for: ' + ', '.join(file_warns) if file_warns else ''}\n"
                f"{'Please select sheets for: ' + ', '.join(sheet_warns) if sheet_warns else ''}")
            return

        # Store selected sheet values
        for k in self.selected_sheets:
            self.selected_sheets[k] = self.sheet_dropdowns[k].get()

        self.update_status("Starting data loading...")
        self.load_button.config(state='disabled')
        self.root.update_idletasks()

        # Setup handler
        handler = AsyncTaskRunner(
            root=self.root,
            task_fn=self.load_all_data,
            args=(self.input_files, self.selected_sheets),
            progress_bar=self.progressbars['load'],
            on_complete=self.handle_load_complete
        )
        self.task_handlers['load'] = handler
        handler.start()


    def handle_load_complete(self, result : dict):
        """ 
        Set up the column dropdowns once data loading has been completed 
        
        Parameters
        ----------
        result : dict
            the loaded in datasets
        """

        self.datasets.update(result)  # Store the loaded data

        # Update column dropdowns
        for key in self.selected_columns:
            if key in self.datasets:
                self.column_options[key] = self.datasets[key].columns.tolist()
                dropdown = self.column_dropdowns[key]
                dropdown.config(state="readonly", values=self.column_options[key])
                dropdown.set('')

        self.update_status("Data loading complete. Please select relevant columns.")
        self.load_button.config(state='normal')
        self.validate_button.config(state="normal")


    @staticmethod
    def validate_all_data(datasets : dict, 
                          selected_columns : dict, 
                          update_callback : Callable=None, 
                          progress_queue : queue.Queue=None):
        """ 
        Performs all validation steps

        This is a three step process:
        1.  Pre-process BOM
        2.  Build product master
        3.  Validate the data
        

        Parameters
        ----------
        datasets : dict
            dictionary containing the datasets to be validated
        selected_columns : dict
            dictionary containing the selected relevant columns
        update_callback : Callable
            function that handles callbacks
        progress_queue : queue.Queue
            progress queue to use for this task

        Returns
        -------
        datasets : dict
            the validated datasets
        """

        if progress_queue:
                progress_queue.put(5)

        # Step 1: Pre-process BOM
        update_callback("Splitting BOM into recipes...") if update_callback else None
        recipes = pre_process_bom(
            datasets['BOM'],
            datasets['Actieve lijst'],
            selected_columns['Actieve lijst']
        )
        datasets['recipes'] = recipes
        progress_queue.put(33.3) if progress_queue else None

        # Step 2: Build product master
        update_callback("Creating product master...") if update_callback else None
        ingredients, packagings, Hfs = process_product_master(recipes)
        datasets['ingredients'] = ingredients
        datasets['packagings'] = packagings
        datasets['Hfs'] = Hfs
        progress_queue.put(66.6) if progress_queue else None

        # Step 3: Run validations
        update_callback("Running data validation...") if update_callback else None
        validate_data(
            ingredients,
            datasets['Prijslijst'],
            selected_columns['Prijslijst'],
            recipes,
            packagings,
            datasets['Waste lijst'],
            update_callback=update_callback
        )
        progress_queue.put(99.9) if progress_queue else None

        return datasets


    def run_data_validation(self):
        """ Trigger threaded data validation task """

        if not all(self.input_files.values()):
            messagebox.showwarning("Missing File", "Please select all 4 input files before running validation.")
            return

        # Ensure column selections are made
        for key in self.selected_columns:
            col = self.column_dropdowns[key].get()
            if not col:
                messagebox.showwarning("Missing Selection", f"Please select a column for: {key}.")
                return
            self.selected_columns[key] = col  # store it

        self.update_status("Starting data validation...")
        self.validate_button.config(state='disabled')
        self.load_button.config(state='disabled')
        self.process_button.config(state='disabled')
        self.root.update_idletasks()

        # Setup thread handler
        handler = AsyncTaskRunner(
            root=self.root,
            task_fn=self.validate_all_data,
            args=(self.datasets, self.selected_columns, self.update_status),
            progress_bar=self.progressbars['validate'],
            on_complete=self.handle_validation_complete,
        )
        self.task_handlers['validate'] = handler
        handler.start()


    def handle_validation_complete(self, updated_datasets : dict):
        """ 
        Called when background validation is done 
        
        updated_datasets : dict
            dictionary containing the validated datasets
        """

        self.datasets = updated_datasets
        self.update_status("Data validation complete. You can now process the data.")
        self.process_button.config(state="normal")
        self.validate_button.config(state='normal')
        self.load_button.config(state='normal')


    def run_processing(self):
        """ Run the full processing """

        self.update_status("Processing... Please wait.")
        self.process_button.config(state="disabled")
        self.validate_button.config(state='disabled')
        self.load_button.config(state='disabled')

        self.task_handlers['process'] = AsyncTaskRunner(
            root=self.root,
            task_fn=process_recipes,
            args=(self.datasets['recipes'],
                self.datasets['ingredients'],
                self.datasets['Hfs'],
                self.datasets['packagings'],
                self.datasets['Prijslijst'],
                self.selected_columns['Prijslijst'],
                req_cols_price_weight[0],
                self.datasets['Prijslijst'],
                self.datasets['Waste lijst']),
                progress_bar=self.progressbars['process'],
            on_complete=self.handle_process_complete
        )

        self.task_handlers['process'].start()

    
    def handle_process_complete(self, result : list):
        """ 
        Save the output from processing once completed

        Parameters
        ----------
        result : list
            the list the results
        """

        recipes = result  # Store results
        self.update_status("Processing complete. Please select where to save output.")

        # Ask for output file location
        output_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Save Output File")
        
        if output_path:
            save_output(recipes=recipes, output_path=output_path)
            self.update_status(f"Output saved to {output_path}")
        else:
            self.update_status("Output saving cancelled.")

        self.process_button.config(state="normal")
        self.validate_button.config(state='normal')
        self.load_button.config(state='normal')


    def update_status(self, message : str):
        """ 
        Helper function to update the status display
        
        Parameters
        ----------
        message : str
            the message to be displayed
        """

        self.status_text.config(state="normal")
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state="disabled")
        self.root.update_idletasks()


if __name__ == "__main__":
    root = tk.Tk()
    app = OKM_processing(root)
    root.mainloop()