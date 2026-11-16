import { createFormHook } from '@tanstack/react-form'

import {
  ChipsField,
  CountryChipsField,
  LanguageRowsField,
  SearchableSelectField,
  SelectField,
  SliderField,
  SubscribeButton,
  TextArea,
  TextField,
  TriStateSwitchField,
  WorkAuthRowsField,
} from '../components/career-form-fields'
import { fieldContext, formContext } from './form-contexts'

export const { useAppForm } = createFormHook({
  fieldComponents: {
    TextField,
    SelectField,
    SearchableSelectField,
    SliderField,
    ChipsField,
    CountryChipsField,
    LanguageRowsField,
    WorkAuthRowsField,
    TriStateSwitchField,
    TextArea,
  },
  formComponents: {
    SubscribeButton,
  },
  fieldContext,
  formContext,
})
