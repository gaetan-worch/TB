import dashboard_client, rtde_io 
from rtde_receive import RTDEReceiveInterface

from enum import Enum
import time, re
import apps.recombination.calculs as calculs

class Robot() :
    """
    A class to interface with a robotic system using RTDE.
    
    Provides functionalities to connect, disconnect, load and execute programs, and 
    perform specific tasks such as picking and placing vials, picking well plates, 
    and handling paradox objects.
    """

    class Register(Enum) :
        """Enum representing the robot registers for offsets."""
        offset_y_well_plate = 18
        offset_x_well_plate = 19
        offset_y_reactor = 20
        offset_x_reactor = 21

    class Programs(Enum) : 
        """Enum representing the available URP programs for the robot."""
        pick_and_place_microvials = "pick_place_vials.urp"
        move_home_from_wellplate = "move_over_vial_to_home.urp"
        move_over_wellplate_from_home = "move_home_to_over_wellplate.urp"
        give_wellplate = "give_wellplate.urp"
        pick_wellplate = "pick_wellplate.urp"
        pick_paradox = "pick_paradox.urp"
        give_paradox = "give_paradox.urp"

    class Status(Enum) :
        """Enum representing robot status."""
        RUN = 1
    
    def __init__(self, ip, **kwargs) :
        """
        Initializes the Robot instance.
        
        Args:
            ip (string): The IP address of the robot.
            kwargs: Optional parameters (e.g., attempts, delay).
        
        Returns:
            None
        """
        self.ip = ip
        self.rtde_d = dashboard_client.DashboardClient(self.ip)
        try :
            self.connection()
        except :
            raise
        self.attempts = kwargs.get("attempts", 3)
        self.delay = kwargs.get("delay", 1)
        self.rtdeReceive = RTDEReceiveInterface(self.ip)
        self.rtdeIO = rtde_io.RTDEIOInterface(self.ip)

    def connection(self) : 
        """
        Establishes a connection with the robot.
        
        Args:
            None
        
        Return:
            None
        """
        print("Connection ....")
        try :
            self.rtde_d.connect()

        except Exception as e :
            print(f"Connection error :\n{e}")
            raise
        print(f"Connection with the robot (ip : {self.ip}) is established")
    
    def disconnection(self) :
        """
        Establishes a connection with the robot.
        
        Args:
            None
        
        Return:
            None
        """
        try : 
            self.rtdeIO.disconnect()
            self.rtdeReceive.disconnect()
            self.rtde_d.disconnect()
        except Exception as e : 
            print(f"Disconnection error :\n{e}")
        print("Robot disconnected")
    
    def __load_program__(self, program_name, nbre_attempts, delay) :
        """
        Loads a URP program onto the robot.
        
        Args :
            program_name (string): Name of the program to load.
            nbre_attempts (int): Number of retry attempts.
            delay (int): Delay between retries.
        
        Return :
            None
        """

        for attempt in range(nbre_attempts) :
            try :
                print(f"Program loading : {program_name}")
                self.rtde_d.loadURP(program_name)
                time.sleep(1)
                loaded_program = re.split("[/]", self.rtde_d.getLoadedProgram())[-1]
                if not (loaded_program == program_name) :
                    raise Exception("Bad program loading")
                print(f"Program \'{program_name}\' successfully loaded.")
                break
            except : 
                print("Error loading program")
                if attempt < nbre_attempts -1 :
                    print(f"New attempt in {delay} seconds.")
                    time.sleep(delay)
                else :
                    print("Too many failed attempts")
                    raise Exception(f"Loading program :  {program_name}: Too many attempts")

    def __run_program__(self, nbre_attempts, delay) :
        """
        Runs the loaded program on the robot.

        Args :
            nbre_attempts (int) : Number of retry attempts.
            delay (int) : Delay between retries.
        
        Return :
            None
        """
        for attempt in range(nbre_attempts) :
            try : 
                self.rtde_d.play()
                
                time.sleep(1)
                while self.rtde_d.running() : 
                    time.sleep(1)
                
                print("Program completed")
                return
            except : 
                print("Error during execution.")
                if attempt < nbre_attempts - 1 :
                    print(f"New attempt in {delay} second.")
                    time.sleep(1)
                else : 
                    print(f"Too many faile attempts")
                    raise Exception("Playing program : ")

    def _load_run_program(self, program_name, nbre_attempts, delay) : 
        """
        Loads and runs a given program.
        
        Args : 
            program_name (string) : Name of the program to execute.
            nbre_attempts (int) : Number of retry attempts.
            delay (int) : Delay between retries.
        """
        try : 
            self.__load_program__(program_name, nbre_attempts, delay)
            self.__run_program__(nbre_attempts, delay)
        except Exception as e :
            print(f"Error : {e}")
            raise

    def __set_attempt__(self, nbre_attempts = None) :
        """
        Set the number of attempts

        Args :
            nbre_attempts (int) : Number of retry attempts. (None by default)
        
        Return :
            nbre_attempts (int) : Number of retry attempts.
        """
        if nbre_attempts == None :
            nbre_attempts = self.attempts
        return nbre_attempts
    
    def __set_delay__(self, delay = None) :
        """
        Set the number of attempts

        Args :
            delay (int) : Delay between retries. (None by default)
        
        Return :
            delay (int) : Delay between retries.
        """
        if delay == None : 
            delay = self.delay
        return delay

    def __set_parameters__(self, nbre_attempts = None, delay = None) : 
        """
        Set the differents parameter (nbre_attempts and delay)

        Args : 
            nbre_attempts (int) : Number of retry attempts. (None by default)
            delay (int) : Delay between retries. (None by default)
        
        Return :
            nbre_attempts (int) : Number of retry attempts.
            delay (int) : Delay between retries.
        """
        return self.__set_attempt__(nbre_attempts), self.__set_delay__(delay)
        
    def pick_wellplate(self, nbre_attempts = None, delay = None) :
        """
        Executes the 'pick_wellplate' program on the robot.
        
        Args : 
            nbre_attempts (int) : Number of retry attempts. (None by default)
            delay (int) : Delay between retries. (None by default)
        
        Return :
            None
        """
        nbre_attempts, delay = self.__set_parameters__(nbre_attempts, delay)
        self._load_run_program(self.Programs.pick_wellplate.value, nbre_attempts, delay)

    def give_wellpalte(self, nbre_attempts = None, delay = None) :
        """
        Executes the 'give_wellplate' program on the robot.
        
        Args : 
            nbre_attempts (int) : Number of retry attempts. (None by default)
            delay (int) : Delay between retries. (None by default)
        
        Return :
            None
        """
        nbre_attempts, delay = self.__set_parameters__(nbre_attempts, delay)
        self._load_run_program(self.Programs.give_wellplate.value, nbre_attempts, delay)

    def pick_and_place_vials(self, positions, nbre_attempts = None, delay = None) :
        """
        Executes the 'pick_and_place' program on the robot.
        
        Args : 
            nbre_attempts (int) : Number of retry attempts. (None by default)
            delay (int) : Delay between retries. (None by default)
        
        Return :
            None
        """
        nbre_attempts, delay = self.__set_parameters__(nbre_attempts, delay)
        self._load_run_program(self.Programs.move_over_wellplate_from_home.value, nbre_attempts, delay)
        
        for pos_vial, pos_reactor in positions :
            print(pos_vial)
            letter_vial, number_vial = calculs.split_letter_number(pos_vial)
            letter_reactor, number_reactor = calculs.split_letter_number(pos_reactor)
            
            offset_x_vial, offset_y_vial = calculs.calcul_position_vial(number_vial, calculs.convert_letter_to_int(letter_vial))
            offset_x_reactor, offset_y_reactor = calculs.calcul_position_reactor(number_reactor, calculs.convert_letter_to_int(letter_reactor))
            
            self.write_double_register(offset_x_vial, self.Register.offset_x_well_plate.value)
            self.write_double_register(offset_y_vial, self.Register.offset_y_well_plate.value)
            self.write_double_register(offset_x_reactor, self.Register.offset_x_reactor.value)
            self.write_double_register(offset_y_reactor, self.Register.offset_y_reactor.value)

            self._load_run_program(self.Programs.pick_and_place_microvials.value, nbre_attempts, delay)

        self._load_run_program(self.Programs.move_home_from_wellplate.value, nbre_attempts, delay)
    
    def pick_paradox(self, nbre_attempts = None, delay = None) :
        """
        Executes the 'pick_paradox' program on the robot.
        
        Args : 
            nbre_attempts (int) : Number of retry attempts. (None by default)
            delay (int) : Delay between retries. (None by default)
        
        Return :
            None
        """
        nbre_attempts, delay = self.__set_parameters__(nbre_attempts, delay)
        self._load_run_program(self.Programs.pick_paradox.value, nbre_attempts, delay)

    def give_paradox(self, nbre_attempts = None, delay = None) :
        """
        Executes the 'give_paradox' program on the robot.
        
        Args : 
            nbre_attempts (int) : Number of retry attempts. (None by default)
            delay (int) : Delay between retries. (None by default)
        
        Return :
            None
        """
        nbre_attempts, delay = self.__set_parameters__(nbre_attempts, delay)
        self._load_run_program(self.Programs.give_paradox.value, nbre_attempts, delay)

    def write_double_register(self, data, register) : 
        """
        Writes a floating-point value to the specified robot register.
        
        Args : 
            data (float) : The value to write.
            register (int) : The register adress.
        
        Return :
            None
        """
        status = self.rtdeIO.setInputDoubleRegister(register, data)
        if not status :
            raise Exception(f"Write data in register {register} failed")