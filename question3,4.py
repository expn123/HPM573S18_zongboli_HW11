import scr.MarkovClasses as MarkovCls
import question1 as matrixdata
import scr.RandomVariantGenerators as rndClasses
import scr.EconEvalClasses as EconCls
from enum import Enum
import Question2 as matrixdatat



delta_t=0.25
Discount_Rate=0.03

rate_matrix_wotherapy=[[None,matrixdata.lambda1,0,matrixdata.lambda2,matrixdata.non_stroke_deathrate],
                       [0,None,matrixdata.rate_stroke_post,0,0],
                        [0,matrixdata.rate_poststr_stroke,None,matrixdata.rate_poststr_strokedeath,matrixdata.non_stroke_mortality],
                        [0,0,0,None,0],
                        [0,0,0,0,None]]
prob_matrixwotherapy=MarkovCls.continuous_to_discrete(rate_matrix_wotherapy,delta_t)

rate_matrix_wtherapy=[[None,matrixdata.lambda1,0,matrixdata.lambda2,matrixdata.non_stroke_deathrate],
                       [0,None,matrixdata.rate_stroke_post,0,0],
                        [0,matrixdatat.rate_poststr_stroke_withtherapy,None,matrixdata.rate_poststr_strokedeath,matrixdatat.therapy_non_stroke_deathrate],
                        [0,0,0,None,0],
                        [0,0,0,0,None]]
prob_matrixwtherapy=MarkovCls.continuous_to_discrete(rate_matrix_wtherapy,delta_t)

TRANS=[prob_matrixwotherapy[0],prob_matrixwtherapy[0]]

TRANS_UTILITY= [
    [1,0.2,0.9,0,0],
    [1,0.2,0.9,0,0]
]

TRANS_COST=[
    [0,5000,200,0,0],
    [0,5000,750,0,0]
]


class HealthStats:
    """ health states of patients with risk of stroke """
    WELL = 0
    STROKE = 1
    P_STROKE = 2
    sDEATH = 3
    Non_Sdeath=4

class THERAPY_OR_NOT (Enum):
    WITHOUT=0
    WITH=1


class Patient:
    def __init__(self, id, THERAPY):
        """ initiates a patient
        :param id: ID of the patient
        :param parameters: parameter object
        """

        self._id = id
        # random number generator for this patient
        self._rng = None
        self.healthstat=0
        self.survival=0
        self.THERAPY = THERAPY
        self.STROKE=0
        self.totalDiscountUtility=0
        self.totalDiscountCost=0


    def simulate(self, sim_length):
        """ simulate the patient over the specified simulation length """

        # random number generator for this patient
        self._rng = rndClasses.RNG(self._id)

        k = 0  # current time step

        # while the patient is alive and simulation length is not yet reached
        while (self.healthstat!=3 or self.healthstat!=4) and k*delta_t< sim_length:
            # find the transition probabilities of the future states
            trans_probs = TRANS[self.THERAPY][self.healthstat]
            # create an empirical distribution
            empirical_dist = rndClasses.Empirical(trans_probs)
            # sample from the empirical distribution to get a new state
            # (returns an integer from {0, 1, 2, ...})
            new_state_index = empirical_dist.sample(self._rng)
            if self.healthstat==1:
                self.STROKE+=1
            #caculate cost and utality
            cost=TRANS_COST[self.THERAPY][self.healthstat]*delta_t
            utility=TRANS_UTILITY[self.THERAPY][self.healthstat]*delta_t
            # update total discounted cost and utility (corrected for the half-cycle effect)
            self.totalDiscountCost += \
                EconCls.pv(cost, Discount_Rate*delta_t, k + 1)
            self.totalDiscountUtility += \
                EconCls.pv(utility, Discount_Rate*delta_t, k + 1)
            # update health state
            self.healthstat =new_state_index[0]
            # increment time step
            k += 1
        self.survival=k*delta_t

    def get_survival_time(self):
        """ returns the patient's survival time"""
        return self.survival

    def get_STROKE_time(self):
        """ returns the patient's survival time"""
        return self.STROKE

    def get_total_utility(self):
        return self.totalDiscountUtility

    def get_total_cost(self):
        return self.totalDiscountCost

class Cohort():
    def __init__(self,id,THERAPY):
        self._initial_pop_size=2000
        self.survivaltime=[]
        self.id=id
        self.THERAPY=THERAPY
        self.STROKE=[]
        self.totaldiscountedcost=[]
        self.totaldiscountedutility=[]

    def simulate(self):
        for i in range(self._initial_pop_size):
            patient=Patient(self.id*self._initial_pop_size+i,self.THERAPY)
            patient.simulate(15)
            self.survivaltime.append(patient.get_survival_time())
            self.STROKE.append(patient.get_STROKE_time())
            self.totaldiscountedcost.append(patient.get_total_cost())
            self.totaldiscountedutility.append(patient.get_total_utility())

    def get_survival_time(self):
        return self.survivaltime

    def get_STROKE_time(self):
        """ returns the patient's survival time"""
        return self.STROKE

    def get_total_utility(self):
        return self.totaldiscountedutility

    def get_total_cost(self):
        return self.totaldiscountedcost

cohort_ONE=Cohort(2,THERAPY_OR_NOT.WITHOUT.value)
cohort_ONE.simulate()

cohort_TWO=Cohort(4,THERAPY_OR_NOT.WITH.value)
cohort_TWO.simulate()

def report_CEA():
    """ performs cost-effectiveness and cost-benefit analyses
    :param simOutputs_mono: output of a cohort simulated under mono therapy
    :param simOutputs_combo: output of a cohort simulated under combination therapy
    """

    # define two strategies
    without_therapy= EconCls.Strategy(
        name='Without Therapy',
        cost_obs=cohort_ONE.get_total_cost(),
        effect_obs=cohort_ONE.get_total_utility()
    )
    with_therapy= EconCls.Strategy(
        name='With Therapy',
        cost_obs=cohort_TWO.get_total_cost(),
        effect_obs=cohort_TWO.get_total_utility()
    )

    # do CEA
    CEA = EconCls.CEA(
        strategies=[without_therapy, with_therapy],
        if_paired=False
    )
    # show the CE plane
    CEA.show_CE_plane(
        title='Cost-Effectiveness Analysis',
        x_label='Additional discounted utility',
        y_label='Additional discounted cost',
        show_names=True,
        show_clouds=True,
        show_legend=True,
        figure_size=6,
        transparency=0.3
    )
    # report the CE table
    CEA.build_CE_table(
        interval=EconCls.Interval.CONFIDENCE,
        alpha=0.05,
        cost_digits=0,
        effect_digits=2,
        icer_digits=2,
    )
report_CEA()
