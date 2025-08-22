#Mengambil library-library yang digunakan
import flet as ft #App ini menggunakan framework flet salah satu frameworkk python
import csv #karena di app ini terhubung ke csv jadi import csv juga
import datetime #mengambil library untuk mengatur penanggalan pada aplikasi
from flet_navigator import VirtualFletNavigator, PageData, ROUTE_404, route

# Class terutama untuk mengatur setiap aspek  di awalnya
class TaskOrganizer(ft.UserControl):
    def did_mount(self):
        #Terpanggil saat class juga dipanggil - menambahkan date picker ke screen
        self.page.overlay.append(self.date_picker)
        self.update()
        
    # fungsi untuk date picker value change
    def change_date(self, e):
        print(f"Date picker changed, value is {self.date_picker.value}")
        self.date_today = self.date_picker.value

    # fungsi untuk ketika date picker ditutup
    def date_picker_dismissed(self, e):
        print(f"Date picker dismissed, value is {self.date_picker.value}")
        self.date_today = self.date_picker.value

    #Membangun komponen UI utama (UI = user interface)        
    def build(self):
        #field input untuk tugas baru
        self.new_task = ft.TextField(hint_text="Whats needs to be done?", expand=True)
        #Container untuk daftar tugas
        self.tasks = ft.Column()    
        #tanggal default (hari ini)
        self.date_today = datetime.date.today()
        #field input untuk link document
        self.link_Docs = ft.TextField(hint_text="Links for google docs", expand=True)
        print('Today date =',self.date_today)
        #mengatur date picker
        self.date_picker = ft.DatePicker(
            on_change=self.change_date,
            on_dismiss=self.date_picker_dismissed,
            
            first_date=datetime.datetime(2023, 10, 1),
            last_date=datetime.datetime(2025, 10, 1),
        )
        
        #Struktur layout utama
        return ft.Column(
            width=800,
            controls=[
                #Baris kontrol atas dengan field input dan tombol
                ft.Row(
                    controls=[
                        self.new_task,
                        self.link_Docs,
                        ft.FloatingActionButton(icon=ft.icons.ADD, on_click=self.add_clicked),
                        ft.ElevatedButton(
                                "Change Task date",
                                icon=ft.icons.CALENDAR_MONTH,
                                on_click=lambda _: self.date_picker.pick_date(),
                        ), 
                        ft.IconButton(
                            ft.icons.FILE_OPEN,
                            tooltip="Open from CSV",
                            on_click=self.csv_open_clicked,
                        ),
                        ft.IconButton(
                            ft.icons.SAVE,
                            tooltip="Save to CSV",
                            on_click=self.csv_save_clicked,
                        ),       
                    ],
                ),
                #Menampilkan tanggal hari ini
                ft.Text('Today Date:'+str(self.date_today)),
                #Container daftar tugas yang bisa di-scroll
                ft.Column(
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    spacing=10,
                    scroll=ft.ScrollMode.ALWAYS,
                    on_scroll_interval=0,
                    height = 500,  
                    controls=[
                        self.tasks,
                    ],
                    
                ),   
            ],
        )
    
    #Menyimpan tugas ke file CSV
    def csv_save_clicked (self,e):
        with open('data.csv', newline='',mode="w") as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)          
            for row in self.tasks.controls:
                str_date = row.date_today.strftime('%Y-%m-%d')
                spamwriter.writerow([row.task_name, row.link_Docs, str_date])
        self.update()
        
    #Membuka tugas dari file CSV    
    def csv_open_clicked (self,e):
        with open('data.csv', newline='',mode="r+") as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                try:     
                    print(row)
                    date_str = row[2]
                    date_format = '%Y-%m-%d'
                    date_obj = datetime.datetime.strptime(date_str.strip(), date_format)
                    task = Task(row[0], self.task_delete,date_obj,row[1], self.task_edit)
                    self.tasks.controls.append(task)
                except Exception as e:
                     print("Data error "+e.args[0])
        self.update()
        
    #Menambahkan tugas baru ke daftar    
    def add_clicked(self, e):
        task = Task(self.new_task.value, self.task_delete,self.date_today,self.link_Docs.value,self.task_edit)
        self.tasks.controls.append(task)
        self.new_task.value = ""
        self.update()
    
    #Mengedit nama tugas yang sudah ada
    def task_edit(self, old_task, task_value):
        for row in self.tasks.controls:
            if old_task == row.task_name:
                row.task_name = task_value
                break
        self.update()   
    
    #Menghapus tugas dari daftar
    def task_delete(self, task):
        self.tasks.controls.remove(task)
        self.update()


#class yang merepresentasikan item tugas individual
class Task(ft.UserControl):
    def __init__(self, task_name, task_delete,date_today,link_Docs,task_edit):
        super().__init__()
        self.task_name = task_name
        self.task_delete = task_delete   
        self.date_today = date_today
        self.link_Docs = link_Docs
        self.task_edit = task_edit   

    #handler event scroll app ke atas dan bawah
    def on_column_scroll(e: ft.OnScrollEvent):
        print(
            f"Type: {e.event_type}, pixels: {e.pixels}, min_scroll_extent: {e.min_scroll_extent}, max_scroll_extent: {e.max_scroll_extent}"
        )
  
    #Membangun komponen UI untuk tugas
    def build(self):
        #Checkbox dengan nama tugas
        self.display_task = ft.Checkbox(value=False, label=self.task_name)
        #field text untuk editing
        self.edit_name = ft.TextField(expand=1)

        #Tampilan utama untuk tugas individual
        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            width=800,
        
            controls=[
                self.display_task,
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.Column(
                            spacing=10,
                            height=200,
                            width=400,
                            scroll=ft.ScrollMode.ALWAYS,
                            on_scroll=self.on_column_scroll,                          
                            controls = [
                                ft.Text('Task Date:'+str(self.date_today)),
                                ft.TextField(
                                    tooltip="Link Docs",
                                    value = str(self.link_Docs),
                                    read_only=True,
                                ),      
                                ft.IconButton(
                                    icon=ft.icons.CREATE_OUTLINED,
                                    tooltip="Edit To-Do",
                                    on_click=self.edit_clicked,
                                ),

                                ft.IconButton(
                                    ft.icons.DELETE_OUTLINE,
                                    tooltip="Delete To-Do",
                                    on_click=self.delete_clicked,
                                ),                      
                            ]
                        ),

                    ],
                ),
            ],
        )

        #Tampilan edit (muncul pas icon edit ditekan)
        self.edit_view = ft.Row(
            visible=False,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.edit_name,
                ft.IconButton(
                    icon=ft.icons.DONE_OUTLINE_OUTLINED,
                    icon_color=ft.colors.GREEN,
                    tooltip="Update To-Do",
                    on_click=self.save_clicked,
                ),
            ],
        )
        return ft.Column(controls=[self.display_view, self.edit_view])
    
    #berpindah ke mode edit
    def edit_clicked(self, e):
        self.edit_name.value = self.display_task.label
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    #Menyimpan perubahan pada tugas
    def save_clicked(self, e):
        self.task_edit(self.display_task.label,self.edit_name.value)
        self.display_task.label = self.edit_name.value
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()
        
    #Menghapus tugas yang ingin dihapus
    def delete_clicked(self, e):
        self.task_delete(self)  

#Halaman instruksi awal
@route('/')
def _page(page: ft.Page):
    page.title = "INSTRUCTIONS" #judul pagenya
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.add( #pengaturan penampilan instruction page
        ft.Column(
            [   
                ft.Container(
                    content=ft.Text(value= " ",color="green",size=25),
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    content=ft.Text(value= " ",color="green",size=25),
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    content=ft.Text(value="MET",
                        color="pink", size=200),
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    content=ft.Text(value= " Your life orginazer",color="yellow",size=25),
                    alignment=ft.alignment.center,
                ),
                ft.Container( #tombol start
                    content=ft.ElevatedButton(text="START", on_click=lambda _: page.navigator.navigate('lobby', page.page)),
                    alignment=ft.alignment.center,
                ),
            ]
        ),
        ft.Container(bgcolor='#75B79E'),
    )
    
#Halaman utama organizer tugas    
@route('lobby')
def lobby(page: ft.Page):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    #Membuat variable untuk menyimpan class TaskOrganizer
    t = TaskOrganizer()    
    
    page.add( #memasukan semua yang sudah kita buat untuk halaman utama ke halamannya
            t,
            ft.Container(
                    content=ft.ElevatedButton(text="Back", on_click=lambda _: page.navigator.navigate('/', page.page)),
                    alignment=ft.alignment.center,
            ),
    )

#Entry point utama aplikasi agar berjalan
def main(page: ft.Page) -> None:
    #Inisialisasi navigator dan render halaman 
    VirtualFletNavigator().render(page)
    page.title = "Organizer Calendar App"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.update()

#Memulai aplikasi
ft.app(main)