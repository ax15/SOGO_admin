#!/usr/bin/env python3

#
# (C) MIT, 2021 ax15
#
__ver__='v1.22'

#
# v1.19 - small changes in main view: wider fields for CN and SOGO CN
#       - added cleanup for sogouser0x0x0x0x00x tables when deleting user
# v1.20 - behaviour of Ctrl+S changed for deleting user only from SOGO database
# v1.21 - fixed user rename: changing name not only in SOGO but in system too
# v1.22 - fix user password update
#

import npyscreen
import psycopg2
import subprocess
import crypt
from hashlib import md5

import logging

logging.basicConfig( format='%(asctime)s %(levelname)s %(filename)s:%(lineno)-4d %(message)s',
                     datefmt='%Y-%m-%d %H:%M:%S',
                     filename='sogo_admin.log',
                     level=logging.WARNING)

logging.critical("="*70)


class SystemUsers(object):
    """ group_filter - is tuple of interesting groups (10,700)"""

    def __init__( self, group_filter ):
        
        self.userlist = {}
        self.default_shell = '/sbin/nologin'
        self.group_filter = group_filter

        with open("/etc/passwd") as passwd:

            logging.info('group filter: %s', self.group_filter )

            for line in passwd.readlines():

                login, nop, uid, gid, uname, home, shell = line.split(':')
                logging.debug('found system user %s group id: %s', login, gid)

                if int(gid) in self.group_filter:
                    self.userlist[login] = ( uid, gid, uname )
                    logging.info('user %s is in interesting group id: %s', login, gid)


    def list_all_users(self):
        return self.userlist


    def get_user(self, c_uid):
        return self.userlist[c_uid]


    def add_user(self, c_uid='', c_password='', c_cn=''):

        if c_uid in self.userlist:
            logging.info("User %s exist in system! Skipping", c_uid)
            return

        crypted_pass = crypt.crypt(c_password, crypt.mksalt(crypt.METHOD_SHA512))

        cmd=['/usr/sbin/useradd','-s','/sbin/nologin','-g','700','-c', c_cn.strip(),'-p', crypted_pass,c_uid]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.debug(cmd)
        output, error = p.communicate()
        output = output.strip().decode("utf-8")
        error = error.decode("utf-8")
        if p.returncode != 0:
            logging.debug(f"E: {error}")
            raise 

        cmd=['/usr/bin/id','-u',c_uid]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = p.communicate()
        output = output.strip().decode("utf-8")
        error = error.decode("utf-8")
        if p.returncode != 0:
            logging.debug(f"E: {error}")
            raise
        uid = output

        logging.info("new user %s uid: %s", c_uid, uid)

        self.userlist[c_uid] = ( uid, '700', c_cn )
        return p.returncode


    def delete_user(self, c_uid):

        cmd=['/usr/sbin/userdel','-r', c_uid]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = p.communicate()
        output = output.strip().decode("utf-8")
        error = error.decode("utf-8")
        if p.returncode != 0:
            logging.debug(f"E: {error}")
        self.userlist.pop(c_uid)
        return p.returncode


    def update_user(self, c_uid, c_password, c_cn):
        
        if c_password == '':
            cmd=['/usr/sbin/usermod', '-c', c_cn, c_uid]

        else:
            crypted_pass = crypt.crypt(c_password, crypt.mksalt(crypt.METHOD_SHA512))
            cmd=['/usr/sbin/usermod','-p', crypted_pass, '-c', c_cn, c_uid]

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = p.communicate()
        output = output.strip().decode("utf-8")
        error = error.decode("utf-8")
        if p.returncode != 0:
            logging.info(f"E: {error}")
            raise

        uid, gid, old_cn = self.userlist[c_uid]
        self.userlist[c_uid]=( uid, gid, c_cn )
        return p.returncode


class UserDatabase(object):
    def __init__(self, hostname="localhost", port="5432", dbname="sogo", user="sogo", passwd="sogo"):

        self.hostname = hostname
        self.port = port
        self.dbname = dbname
        self.user = user
        self.passwd = passwd

        try:
            self.db = psycopg2.connect( user = self.user,
                                   password = self.passwd,
                                   host = self.hostname,
                                   port = self.port,
                                   database = self.dbname )

            logging.debug("%s DB connected", self.dbname)

            with self.db.cursor() as c:
                c.execute( "CREATE TABLE IF NOT EXISTS sogo_users\
                    ( c_uid VARCHAR(255) PRIMARY KEY, \
                      c_name VARCHAR(255), \
                      c_password VARCHAR(32), \
                      c_cn VARCHAR(128), \
                      mail VARCHAR(128) \
                      )" \
                    )
                self.db.commit()

        except (Exception, psycopg2.Error) as error :
            print ("Error while connecting to PostgreSQL", error)


    def add_user(self, c_uid = '', c_name='', c_password='', c_cn='', email_address=''):

        md5_hd = md5( c_password.encode() ).hexdigest()

        # check user existance

        with self.db.cursor() as c:

            c.execute( 'SELECT * FROM sogo_users WHERE c_uid=%s', (c_uid,))
            if c.fetchone():
                logging.info("User %s exist in SOGO db!", c_uid)
                return

        with self.db.cursor() as c:

            c.execute( 'INSERT INTO sogo_users \
                        VALUES (%s,%s,%s,%s,%s)', (c_uid.strip(), c_name.strip(), md5_hd, c_cn.strip(), email_address.strip()))

            self.db.commit()



    def update_user(self, c_uid, c_name='', c_password='', c_cn='', email_address=''):
       
        if c_password != '':
 
            md5_hd = md5( c_password.encode() ).hexdigest()
            with self.db.cursor() as c:

                c.execute( 'UPDATE sogo_users SET c_name=%s, c_password=%s, c_cn=%s, mail=%s \
                            WHERE c_uid=%s', (c_name.strip(), md5_hd, c_cn.strip(), email_address.strip(), c_uid.strip()))

        else:
            
            with self.db.cursor() as c:
                
                c.execute( 'UPDATE sogo_users SET c_name=%s, c_cn=%s, mail=%s \
                            WHERE c_uid=%s', (c_name.strip(), c_cn.strip(), email_address.strip(), c_uid.strip()))
        
        logging.debug("cursor exec updated %d rows", c.rowcount )
        self.db.commit()


    def delete_user(self, c_uid):
        with self.db.cursor() as c:
            c.execute('SELECT table_name FROM information_schema.tables\
                       WHERE  table_name like %s\
                       AND table_schema not in (\'information_schema\', \'pg_catalog\') \
                       AND table_type = \'BASE TABLE\'', ('sogo'+c_uid+'%',))
            tables_to_delete = c.fetchall()
            logging.warning("Those tables will be deleted also: %s", tables_to_delete)

        with self.db.cursor() as c:
            for table in tables_to_delete:
                logging.warning('Dropping table: %s', table)
                c.execute('DROP TABLE {} CASCADE'.format(table[0]) )

        with self.db.cursor() as c:

            c.execute('DELETE FROM sogo_users WHERE c_uid=%s', (c_uid,))
            logging.info("deleting user: %s", c.rowcount)

            c.execute('DELETE FROM sogo_folder_info WHERE c_path2=%s', (c_uid,))
            logging.info("deleting folders: %s ", c.rowcount)

            c.execute('DELETE FROM sogo_user_profile WHERE c_uid=%s', (c_uid,))
            logging.info("deleting user profile settings: %s ", c.rowcount)

            self.db.commit()


    def list_user_table(self, ):
        with self.db.cursor() as c:

            c.execute('SELECT * from sogo_users')
            users = c.fetchall()

        return users


    def list_all_users(self, ):
        user_dict = {}

        with self.db.cursor() as c:

            c.execute('SELECT * from sogo_users')
            users = c.fetchall()


        # convert tuple into dictionary
        for user in users:

            c_uid, c_name, c_password, c_cn, email_address = user
            user_dict[c_uid] = (c_name, c_password, c_cn, email_address)

        return user_dict


    def get_user(self, c_uid):
        with self.db.cursor() as c:
        
            c.execute('SELECT * from sogo_users WHERE c_uid=%s', (c_uid,))
            user = c.fetchone()

        return user



class UserList(npyscreen.MultiLineAction):
    def __init__(self, *args, **keywords):
        super(UserList, self).__init__(*args, **keywords)
        self.add_handlers({
            "^A": self.when_add_user,
            "^D": self.when_delete_user,
            "^O": self.when_import,
            "^Q": self.when_quit,
            "^H": self.when_help,
            "^S": self.when_delete_sogo_user
        })

    def display_value(self, vl):
        prep_line="{:>4} {:>25}  {:5} {:<5}  {:32} {:32} {:20}"
        logging.debug("vl: %s", vl)
        return prep_line.format( *vl )


    def actionHighlighted(self, act_on_this, keypress):
        if act_on_this[0] != 'LNX':
            self.parent.parentApp.getForm('EDITUSERFM').value = act_on_this[1]
            self.parent.parentApp.switchForm('EDITUSERFM')


    def when_add_user(self, *args, **keywords):
        self.parent.parentApp.getForm('EDITUSERFM').value = None
        self.parent.parentApp.switchForm('EDITUSERFM')


    def when_delete_user(self, *args, **keywords):

        message='Are sure? You are going to remove selected user.'

        if npyscreen.notify_ok_cancel( message , title= 'Remove user: '+self.values[self.cursor_line][1] ):

            if self.values[self.cursor_line][0] == 'LS':
                self.parent.parentApp.myDatabase.delete_user( self.values[self.cursor_line][1] )
                self.parent.parentApp.mySystem.delete_user( self.values[self.cursor_line][1] )

            elif self.values[self.cursor_line][0] == 'SOGO':
                self.parent.parentApp.myDatabase.delete_user( self.values[self.cursor_line][1] )

            elif self.values[self.cursor_line][0] == 'LNX':
                self.parent.parentApp.mySystem.delete_user( self.values[self.cursor_line][1] )

        self.parent.update_list()


    def when_import(self, *args, **kwargs):

        self.csv_filename = npyscreen.fmFileSelector.selectFile(
            select_dir = False,
            must_exist = True,
            confirm_if_exists = False,
            sort_by_extension = True )

        logging.info("selected file: %s", self.csv_filename)

        with open(self.csv_filename) as csv_file:

            lines=csv_file.readlines()       

        for line in lines:

            i_uid, i_passwd, i_cn, i_email_address = line.split(',')

            logging.warning("Import new user into SOGO db: %s, '%s'", i_uid, i_email_address.strip() )

            self.parent.parentApp.myDatabase.add_user( c_uid  = i_uid,
                                            c_name     = i_uid,
                                            c_password = i_passwd, 
                                            c_cn       = i_cn, 
                                            email_address = i_email_address )

            logging.info("Import new system user: %s", i_uid)
            self.parent.parentApp.mySystem.add_user( c_uid      = i_uid,
                                            c_password   = i_passwd,
                                            c_cn         = i_cn )

        self.parent.update_list()


    def when_help(self, *args, **kwargs ):
        help_message = ('g      - go to the first user',
                        'G      - go to the last user',
                        'l      - lookup',
                        'Ctrl+A - Add new user',
                        'Ctrl+D - Delete user',
                        'Ctrl+S - Delete user from SOGO DB only',
                        'Ctrl+O - Open csv file for users import',
                        'Enter  - edit current user',
                        'Ctrl+H - this help',
                        'Ctrl+Q - Quit')

        npyscreen.notify_wait( '\n'.join(help_message), title='Usage: ', wide=True )


    def when_delete_sogo_user(self, *args, **kwargs ):
        message='Are sure? You are going to remove selected user.'

        if npyscreen.notify_ok_cancel( message , title= 'Remove user from SOGO DB only: '+self.values[self.cursor_line][1] ):
            if self.values[self.cursor_line][0] == 'LS' or self.values[self.cursor_line][0] == 'SOGO':
                logging.warning("Deleting user from SOGO DB: %s", self.values[self.cursor_line][1])
                self.parent.parentApp.myDatabase.delete_user( self.values[self.cursor_line][1] )

        self.parent.update_list()


    def when_quit(self, *args, **keywords):
        self.parent.parentApp.switchForm(None)



class UserListDisplay(npyscreen.FormMutt):
    MAIN_WIDGET_CLASS = UserList
    MAIN_WIDGET_CLASS_START_LINE = 3

    def beforeEditing(self):
        self.update_list()
        self.header = self.add(npyscreen.FixedText,)
        self.header.relx = 0
        self.header.rely = 1
        self.header.value = "{:>4} {:^25}  {:5} {:<5}  {:32} {:32} {:20}".format('Flag','System/SOGo login','UID','GID','Common Name','CN in SOGo','e-mail')
        self.header.display()
        

    def update_list(self):
        sogo_db_users = self.parentApp.myDatabase.list_all_users()
        system_users = self.parentApp.mySystem.list_all_users()

        set_sogo_db_users_set = set( sogo_db_users.keys() )
        set_system_users = set( system_users.keys() )

        union_users_set = set_system_users | set_sogo_db_users_set

        united_users = tuple()

        for user in union_users_set:

            logging.debug("union user: %s", user)

            if user in sogo_db_users and user in system_users.keys():
                logging.debug("user in both databases: %s", user)
                uid, gid, uname = system_users[user]
                united_users +=  ( ('LS',) + (user , uid, gid, uname) + sogo_db_users[user][2:] ),

            elif user in sogo_db_users and user not in system_users.keys():
                logging.debug("user in sogo_db only: %s", user)
                united_users +=  ( ('SOGO',) + ( sogo_db_users[user][0] ,'','','') + sogo_db_users[user][2:] ),

            elif user in system_users.keys() and user not in sogo_db_users:
                logging.debug("user in system only: %s", user)
                uid, gid, uname = system_users[user]
                united_users += ( ('LNX',) + ( user, uid, gid, uname ) + ('','','') ),

        self.wMain.values = sorted(united_users, key= lambda t: t[1])
        self.wStatus1.value = "MS31 SOGo users " + __ver__ + ' '
        self.wStatus2.value = "Exit: Ctrl-Q | Help: Ctrl-H |"
        self.wMain.display()


class EditUser(npyscreen.ActionPopup):
    
    def create(self):

        self.value = ''
        self.wgC_Name       = self.add(npyscreen.TitleText, name = "Login:")
        self.wgC_Passwd     = self.add(npyscreen.TitlePassword, name = "Password:")
        self.wgC_CN         = self.add(npyscreen.TitleText, name = "Common Name:")
        self.wgEmail        = self.add(npyscreen.TitleText, name = "Email:")
        self.wgCreateInSOGO = self.add(npyscreen.CheckBox, name = "Create user in SOGO DB")

    def beforeEditing(self):

        if self.value:

            user = self.parentApp.myDatabase.get_user(self.value)
            self.name               = user[3]
            self.c_uid              = user[0]
            self.wgC_Name.value     = user[1]
            self.wgC_Passwd.value   = user[2]
            self.wgC_CN.value       = user[3]
            self.wgEmail.value      = user[4]

            # save old password for future comparision
            self.old_passwd         = str(user[2]).encode().decode()

            logging.debug("user %s copy of old hash: %s", self.c_uid, self.old_passwd)

            self.wgC_Name.editable  = False
            self.only_once          = False

        else:

            self.wgC_Name.editable = True

            self.name = "New User"
            self.wgC_Name.value     = ''
            self.wgC_Passwd.value   = ''
            self.wgC_CN.value       = ''
            self.wgEmail.value      = '@' + self.parentApp.default_domain
            self.c_uid              = self.wgC_Name.value
            self.only_once          = True


    def while_editing(self, *args, **keywords):

        if self.wgC_Name.value:

            self.wgC_Name.value = self.wgC_Name.value.replace(' ', '_')
            logging.debug("replace spaces: %s", self.wgC_Name.value)

        logging.debug("while_editing only_once: %s", self.only_once)

        if self.wgC_Name.value and self.only_once:

            logging.debug("only_once: %s, %s", self.wgC_Name.value, self.wgEmail.value)
            self.wgEmail.value = self.wgC_Name.value + '@' + self.parentApp.default_domain
            self.only_once = False


    def on_ok(self):

        logging.debug("OK pressed. c_uid: %s", self.c_uid)

        if self.c_uid:   # We are editing an existing record

            if self.wgC_Passwd.value != self.old_passwd:

                logging.warning("system update user %s", self.c_uid)
                self.parentApp.mySystem.update_user(self.c_uid, c_password=self.wgC_Passwd.value, c_cn=self.wgC_CN.value)
                logging.warning("SOGo update user %s in db", self.c_uid)
                self.parentApp.myDatabase.update_user(self.c_uid,
                                                        c_name        = self.wgC_Name.value,
                                                        c_password    = self.wgC_Passwd.value,
                                                        c_cn          = self.wgC_CN.value,
                                                        email_address = self.wgEmail.value )

            else:

                logging.warning("user %s, password wasn't changed",  self.c_uid)

                self.parentApp.myDatabase.update_user(self.c_uid,
                                            c_name        = self.wgC_Name.value,
                                            c_password    = '',
                                            c_cn          = self.wgC_CN.value,
                                            email_address = self.wgEmail.value )
                self.parentApp.mySystem.update_user(self.c_uid, c_password='', c_cn=self.wgC_CN.value)

        else:

            # We are adding a new record.

            if self.wgCreateInSOGO.value:
                logging.debug("New user: %s ", self.wgC_Name.value)
                self.parentApp.myDatabase.add_user( c_uid    = self.wgC_Name.value,
                                                c_name       = self.wgC_Name.value,
                                                c_password   = self.wgC_Passwd.value,
                                                c_cn         = self.wgC_CN.value,
                                                email_address = self.wgEmail.value )
                                                
            logging.info("create system user")
            self.parentApp.mySystem.add_user( c_uid      = self.wgC_Name.value,
                                            c_password   = self.wgC_Passwd.value,
                                            c_cn         = self.wgC_CN.value )

        self.parentApp.switchFormPrevious()


    def on_cancel(self):
        self.parentApp.switchFormPrevious()



class SOGOUserManager(npyscreen.NPSAppManaged):

    default_domain = "domain.tld"
    # wheel gid:     10
    # mailusers gid: 700
    group_filter   = (10,700) 

    def onStart(self):
        self.myDatabase = UserDatabase()
        self.mySystem = SystemUsers( self.group_filter )
        self.addForm( "MAIN", UserListDisplay )
        self.addForm( "EDITUSERFM", EditUser )


if __name__ == '__main__':
    myApp = SOGOUserManager()
    myApp.run()

